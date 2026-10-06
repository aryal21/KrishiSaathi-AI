import os, re, tempfile, json
os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mkstemp(suffix=".db")[1]
os.environ["SECRET_KEY"] = "test-secret"
import pytest
from fastapi.testclient import TestClient
import main
from db.models import Base, engine, SessionLocal, User, Chat, Message
from services import llm

SIGNUP = dict(name="Ramesh", mobile="9876543210", pin="1234", village="V", district="Nashik", state="Maharashtra",
              land=3, crops=["soybean"], language="hi", voice=False, theme="auto")

@pytest.fixture(autouse=True)
def fresh(monkeypatch):
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine); main.RL.clear()
    monkeypatch.setattr(llm, "chat", lambda s, m, max_tokens=700: "जवाब")
def client(**over):
    c = TestClient(main.app); r = c.post("/api/signup", json={**SIGNUP, **over}); return c, r

def test_signup_validation():
    c = TestClient(main.app)
    for bad in [dict(mobile="12345"), dict(mobile="5876543210"), dict(pin="12"), dict(pin="abcd"), dict(name=""), dict(language="xx"), dict(theme="x"), dict(land=-1)]:
        assert c.post("/api/signup", json={**SIGNUP, **bad}).status_code == 422, bad

def test_signup_login_me_and_pin_is_hashed():
    c, r = client(); assert r.status_code == 200 and "pin" not in r.text
    assert c.get("/api/me").json()["name"] == "Ramesh"
    with SessionLocal() as db: h = db.query(User).one().pin_hash
    assert h != "1234" and h.startswith("$2")
    c2 = TestClient(main.app)
    assert c2.get("/api/me").status_code == 401
    assert c2.post("/api/login", json={"mobile": "9876543210", "pin": "9999"}).status_code == 401
    assert c2.post("/api/login", json={"mobile": "9876543210", "pin": "1234"}).status_code == 200

def test_cookie_flags_and_duplicate():
    c, r = client(); sc = r.headers["set-cookie"].lower(); assert "httponly" in sc and "samesite=lax" in sc
    assert client()[1].status_code == 409

def test_login_throttle():
    client(); c = TestClient(main.app)
    codes = [c.post("/api/login", json={"mobile": "9876543210", "pin": "0000"}).status_code for _ in range(10)]
    assert codes[:8] == [401] * 8 and codes[8] == 429

def test_chat_saves_history_and_profile_in_prompt(monkeypatch):
    seen = {}
    monkeypatch.setattr(llm, "chat", lambda s, m, max_tokens=700: seen.update(s=s, m=m) or "ठीक है")
    c, _ = client(); r = c.post("/api/chat", json={"message": "  नमस्ते  \x00"}); assert r.status_code == 200
    cid = r.json()["chat_id"]; assert "Nashik" in seen["s"] and "soybean" in seen["s"] and "Hindi" in seen["s"] and seen["m"][-1]["content"] == "नमस्ते"
    c.post("/api/chat", json={"message": "फिर?", "chat_id": cid})
    assert len(seen["m"]) == 3 and seen["m"][0]["role"] == "user"
    assert [m["role"] for m in c.get(f"/api/chats/{cid}").json()] == ["user", "assistant"] * 2
    assert c.get("/api/chats").json()[0]["id"] == cid

def test_llm_failure_saves_nothing(monkeypatch):
    def boom(*a, **k): raise llm.LLMError("x")
    monkeypatch.setattr(llm, "chat", boom); c, _ = client()
    assert c.post("/api/chat", json={"message": "hi"}).status_code == 503
    with SessionLocal() as db: assert db.query(Chat).count() == 0 and db.query(Message).count() == 0

def test_llm_without_key_is_clean_error(monkeypatch):
    monkeypatch.undo(); monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(llm.LLMError): llm.chat("s", [{"role": "user", "content": "x"}])

def test_users_cannot_read_each_others_chats():
    a, _ = client(); cid = a.post("/api/chat", json={"message": "secret"}).json()["chat_id"]
    b, _ = client(mobile="9123456780")
    assert b.get(f"/api/chats/{cid}").status_code == 404 and b.get("/api/chats").json() == []
    assert b.post("/api/chat", json={"message": "x", "chat_id": cid}).status_code == 404

def test_chat_validation_and_rate_limit():
    c, _ = client()
    assert c.post("/api/chat", json={"message": ""}).status_code == 422 and c.post("/api/chat", json={"message": "x" * 1001}).status_code == 422
    assert c.post("/api/chat", json={"message": "\x00\x01"}).status_code == 422
    codes = [c.post("/api/chat", json={"message": "hi"}).status_code for _ in range(21)]
    assert codes[-1] == 429 and codes[0] == 200
    assert TestClient(main.app).post("/api/chat", json={"message": "hi"}).status_code == 401

def test_profile_update_and_new_pin():
    c, _ = client(); r = c.put("/api/me", json={**SIGNUP, "name": "Suresh", "language": "mr", "crops": ["wheat"], "new_pin": "5678"}); assert r.json()["name"] == "Suresh"
    assert TestClient(main.app).post("/api/login", json={"mobile": "9876543210", "pin": "5678"}).status_code == 200
    assert c.put("/api/me", json={**SIGNUP, "new_pin": "1"}).status_code == 422

def test_delete_account_removes_everything():
    c, _ = client(); c.post("/api/chat", json={"message": "hi"}); assert c.delete("/api/me").status_code == 200
    with SessionLocal() as db: assert db.query(User).count() == db.query(Chat).count() == db.query(Message).count() == 0
    assert c.get("/api/me").status_code == 401

def test_static_routes_and_i18n_endpoint():
    c = TestClient(main.app)
    for p in ["/", "/sw.js", "/manifest.json", "/privacy", "/static/app.js", "/static/styles.css"]: assert c.get(p).status_code == 200, p
    assert c.get("/api/i18n/hi").json()["app"] and c.get("/api/i18n/xx").status_code == 404 and c.get("/api/i18n/..%2Fmain").status_code == 404

def test_i18n_parity_and_every_used_key_exists():
    d = {l: json.load(open(f"i18n/{l}.json", encoding="utf-8")) for l in ["en", "hi", "mr"]}
    assert set(d["hi"]) == set(d["mr"]) == set(d["en"]) and all(v.strip() for l in d.values() for v in l.values())
    src = open("static/app.js", encoding="utf-8").read() + open("static/index.html", encoding="utf-8").read()
    used = set(re.findall(r'\bt\("(\w+)"\)', src)) | set(re.findall(r'data-i18n="(\w+)"', src)) | set(re.findall(r'"(wq\d)"', src))
    assert used and used <= set(d["en"]), used - set(d["en"])
    assert {"err_" + e for e in ["invalid_credentials", "mobile_exists", "rate_limited", "llm_unavailable", "not_logged_in", "invalid", "not_found"]} <= set(d["en"])
