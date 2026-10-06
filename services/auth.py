"""PIN hashing (bcrypt) and signed session tokens (JWT in an HTTP-only cookie)."""
import os, secrets, time
import bcrypt, jwt

SECRET = os.getenv("SECRET_KEY") or secrets.token_hex(32)  # no SECRET_KEY => sessions reset on restart
def hash_pin(pin): return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
def check_pin(pin, h): return bcrypt.checkpw(pin.encode(), h.encode())
def make_token(uid): return jwt.encode({"sub": str(uid), "exp": int(time.time()) + 7 * 86400}, SECRET, "HS256")
def read_token(tok):
    try: return int(jwt.decode(tok, SECRET, ["HS256"])["sub"])
    except Exception: return None
