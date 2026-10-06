"""Verify live server endpoints on http://127.0.0.1:8000"""
import urllib.request
import json

# 1. Test index page
req = urllib.request.urlopen("http://127.0.0.1:8000/")
html = req.read().decode("utf-8")
assert "KrishiSaathi AI" in html
assert "FRESH FARMING TOWARD STEADY GROWTH" in html
assert "GET STARTED" in html
assert "Market Access Support" in html
print("[OK] Index HTML loaded & contains Image 1 Hero elements")

# 2. Test static assets
css = urllib.request.urlopen("http://127.0.0.1:8000/static/styles.css").read().decode("utf-8")
assert "--primary" in css
print("[OK] Static CSS loaded successfully")

js = urllib.request.urlopen("http://127.0.0.1:8000/static/app.js").read().decode("utf-8")
assert "enterApp" in js
print("[OK] Static JavaScript app loaded successfully")

# 3. Test i18n
for lang in ["hi", "mr", "en", "pa", "gu"]:
    data = json.loads(urllib.request.urlopen(f"http://127.0.0.1:8000/api/i18n/{lang}").read().decode("utf-8"))
    assert "app" in data
print("[OK] Multi-language i18n endpoints verified")

# 4. Test Mandi prices
mandi_res = urllib.request.urlopen("http://127.0.0.1:8000/api/mandi-prices?crop=Soybean")
mandi_data = json.loads(mandi_res.read().decode("utf-8"))
assert len(mandi_data["mandis"]) >= 5
assert "recommendation" in mandi_data
print(f"[OK] Mandi Prices endpoint verified ({len(mandi_data['mandis'])} mandis returned, AI profit tip present)")

# 5. Test Weather
weather_res = urllib.request.urlopen("http://127.0.0.1:8000/api/weather")
weather_data = json.loads(weather_res.read().decode("utf-8"))
assert len(weather_data["forecast"]) == 7
print("[OK] 7-Day Hyperlocal Weather forecast verified")

print("\nALL LIVE SERVER CHECKS PASSED PERFECTLY!")
