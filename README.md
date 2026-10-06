# 🌾 KrishiSaathi AI - Production Progressive Web App

An AI-powered agricultural companion designed for Indian farmers to solve 5 critical challenges:
1. **💸 Debt Trap Relief**: Loan optimizer highlighting KCC 4% subsidized rates vs 36% moneylenders.
2. **🏥 Zero-Rejection Insurance**: Auto-fills Pradhan Mantri Fasal Bima Yojana (PMFBY) claim forms with 72-hour SLA tracking.
3. **🌱 Anti-Counterfeit Verification**: Validates seeds and chemicals against authorized manufacturer databases (Bayer, IFFCO, Syngenta, UPL).
4. **🏪 Fair Mandi Price Discovery**: APMC rate comparison across 10 nearest markets with AI profit-routing recommendations.
5. **😔 Mental Health & Farmer Wellness**: Mind Mitra counseling, mood tracker, and instant 24/7 crisis helplines.

---

## 🎨 Design System
- **Hero Landing (Image 1 Style)**: Cinematic agricultural landscape, "FRESH FARMING TOWARD STEADY GROWTH", modern pill button `[GET STARTED ➔]`, trust proof badge `50K+ Farms supported`, and 3 bottom teaser features.
- **Slide-to-Login Portal**: Smooth transition into side-by-side Login & Signup on the exact same immersive background. Includes a 1-click Demo Account button (`9876543210` / `1234`).
- **Main Dashboard (Image 2 EcoFarm Style)**: Ultra-clean agriculture design, welcome hero banner with active farmer metrics, 9 interactive feature modules, impact metrics bar, farmer testimonials, and service showcase.
- **AI Chatbot (Always Accessible)**: Right column assistant with dynamic user greeting, 7 quick suggestion chips, Web Speech voice input (🎤), speech synthesis playback (🔊), and chat history.
- **9 Indian Languages**: Hindi (हिंदी), Marathi (मराठी), Punjabi (ਪੰਜਾਬੀ), Gujarati (ગુજરાતી), Tamil (தமிழ்), Telugu (తెలుగు), Kannada (ಕನ್ನಡ), Bengali (বাংলা), English.
- **Light & Dark Theme Toggle**: Instant switching with CSS design tokens.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Development Server
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

### 3. Run Automated Tests
```bash
pytest tests/ -v
```
All 21 unit & feature tests pass automatically.

---

## 🔑 Demo Account
For 1-click evaluation:
- **Phone**: `9876543210`
- **PIN**: `1234` (or `demo123`)
- **Farmer Name**: `Ramesh Patil`
- **Location**: `Dindori, Nashik (Maharashtra)`

---

## 📱 Features Implemented
1. **📸 Crop Disease Detection**: Visual leaf analysis, confidence score, severity rating, ICAR protocol, organic & chemical sprays, estimated cost, and downloadable official PDF diagnostic report.
2. **🏥 PMFBY Insurance Claim Wizard**: 5-step interactive wizard, pre-filled farmer data, 72-hour window alert, loss payout calculation, and downloadable official claim receipt PDF.
3. **💸 Loan Optimizer**: Interactive slider for principal and tenure, comparison of 5 institutional schemes (KCC 4%, SBI 8.5%, Bank of Baroda 8.25%, NABARD 9.0%, Moneylender 36%), and interest savings calculator.
4. **🏪 Mandi Prices**: Real-time prices across 10 nearest APMC mandis for Soybean, Cotton, Wheat, and Onion, with AI profit opportunity analysis.
5. **🌱 Product Verification**: Batch verification against verified manufacturer databases, community feedback aggregation, genuine/fake verdicts, authorized dealers list, and auto-generated District Agriculture Officer complaint PDF.
6. **🌾 Crop Production Advisor**: Scientific fertilizer schedule (Urea, DAP, MOP), irrigation stages, month-wise calendar, and economic return projections.
7. **🌦️ Hyperlocal Weather Advisory**: 7-day forecast, severe rain warnings (>50mm), and crop-specific alerts.
8. **🗣️ Voice Diagnosis**: Natural language speech-to-text input (🎤) and spoken audio responses (🔊).
9. **😔 Mind Mitra**: Daily mood logging, empathetic chat guidance, and 24/7 toll-free crisis helpline intervention (1800-180-1551, 14416, 022-25521111, 9820466726).

---

## 🚢 Deployment to Hugging Face Spaces (CPU Tier, Free)
Create a new Space on Hugging Face with the **Docker** or **FastAPI** SDK, and upload the repository files.

### Hugging Face Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```
