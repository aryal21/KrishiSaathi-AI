"""Tests for KrishiSaathi AI 9 core agricultural features, PDF generation, and farm profiles."""
import io
import json
import os
import tempfile
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mkstemp(suffix=".db")[1]
os.environ["SECRET_KEY"] = "feature-test-secret"

import main
from db.models import Base, engine, SessionLocal, User

SIGNUP = dict(
    name="Ramesh Patil",
    mobile="9876543210",
    pin="1234",
    village="Dindori",
    district="Nashik",
    state="Maharashtra",
    land=3.5,
    crops=["soybean", "wheat"],
    language="hi",
    voice=False,
    theme="light"
)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    main.RL.clear()

def auth_client():
    c = TestClient(main.app)
    r = c.post("/api/signup", json=SIGNUP)
    assert r.status_code == 200
    return c

def test_disease_detection():
    c = auth_client()
    res = c.post("/api/disease-check", json={"sample_key": "soybean_mosaic", "crop": "Soybean"})
    assert res.status_code == 200
    data = res.json()
    assert "Yellow Mosaic" in data["disease"]
    assert data["confidence"] > 80
    assert "treatment" in data

    # Test PDF generation
    pdf_res = c.post("/api/disease/pdf", json=data)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000

def test_product_verification():
    c = auth_client()
    res_gen = c.post("/api/product-verify", json={"batch_no": "BY-9042", "company": "Bayer", "product_name": "Confidor"})
    assert res_gen.status_code == 200
    assert "Genuine" in res_gen.json()["status"]

    res_fake = c.post("/api/product-verify", json={"batch_no": "FAKE-999", "company": "Unknown", "product_name": "FakeChem"})
    assert res_fake.status_code == 200
    assert "Fake" in res_fake.json()["status"]

    complaint_res = c.post("/api/product/complaint-pdf", json={"batch_no": "FAKE-999", "company": "Bad Dealer", "product_name": "Counterfeit Pesticide"})
    assert complaint_res.status_code == 200
    assert complaint_res.headers["content-type"] == "application/pdf"

def test_insurance_claims():
    c = auth_client()
    claim_in = {
        "crop": "Soybean",
        "survey_number": "48/B",
        "land_acres": 2.5,
        "loss_cause": "Unseasonal Torrential Rain",
        "loss_percentage": 60
    }
    submit_res = c.post("/api/claims", json=claim_in)
    assert submit_res.status_code == 200
    claim_id = submit_res.json()["claim_id"]
    assert claim_id.startswith("PMFBY-")

    list_res = c.get("/api/claims")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    pdf_res = c.get(f"/api/claims/{claim_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"

def test_loans_calculator():
    c = auth_client()
    res = c.post("/api/loans/calculate", json={"principal": 150000, "tenure_years": 3, "category": "crop_kcc"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["schemes"]) >= 5
    assert data["schemes"][0]["annual_rate"] == 4.0

def test_mandi_prices():
    c = auth_client()
    res = c.get("/api/mandi-prices?crop=Soybean")
    assert res.status_code == 200
    data = res.json()
    assert len(data["mandis"]) >= 4
    assert "recommendation" in data

def test_crop_advisor():
    c = auth_client()
    res = c.post("/api/crop-advisor", json={"crop": "Soybean", "acres": 3.0, "soil_type": "Black soil"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["fertilizer_schedule"]) >= 3
    assert "economics" in data

def test_weather():
    c = auth_client()
    res = c.get("/api/weather?district=Nashik&state=Maharashtra")
    assert res.status_code == 200
    data = res.json()
    assert len(data["forecast"]) == 7

def test_mood_and_crisis():
    c = auth_client()
    res = c.post("/api/mood", json={"mood": "Sad", "score": 3, "category": "Crop Loss", "note": "Worrying about rain"})
    assert res.status_code == 200
    hist = c.get("/api/mood/history")
    assert hist.status_code == 200
    assert len(hist.json()["helplines"]) >= 4
