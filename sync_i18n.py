"""Script to guarantee 100% key parity across all language JSON files."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
i18n_dir = os.path.join(HERE, "i18n")

base_keys = {
    "app": ("KrishiSaathi AI", "कृषि सार्थी AI", "कृषी सार्थी AI"),
    "tagline": ("Farmers' AI companion", "भारतीय किसानों का AI साथी", "शेतकऱ्यांचा AI सोबती"),
    "login": ("Login", "लॉगिन", "लॉगिन"),
    "signup": ("Sign up", "नया खाता", "नवीन खाते"),
    "logout": ("Log out", "लॉग आउट", "बाहेर पडा"),
    "mobile": ("Mobile number", "मोबाइल नंबर", "मोबाईल नंबर"),
    "pin": ("PIN (4-6 digits)", "पिन (4-6 अंक)", "पिन (4-6 अंक)"),
    "name": ("Name", "नाम", "नाव"),
    "village": ("Village", "गांव", "गाव"),
    "district": ("District", "जिला", "जिल्हा"),
    "state": ("State", "राज्य", "राज्य"),
    "land": ("Land (acres)", "जमीन (एकड़)", "जमीन (एकर)"),
    "crops": ("Main crops", "मुख्य फसलें", "प्रमुख पिके"),
    "language": ("Language", "भाषा", "भाषा"),
    "voice": ("Voice mode", "आवाज़ मोड", "आवाज मोड"),
    "theme": ("Theme", "थीम", "थीम"),
    "auto": ("Auto", "सिस्टम", "सिस्टम"),
    "light": ("Light", "लाइट", "लाइट"),
    "dark": ("Dark", "डार्क", "डार्क"),
    "save": ("Save", "सुरक्षित करें", "जतन करा"),
    "saved": ("Saved", "सुरक्षित हुआ", "जतन झाले"),
    "hello": ("Namaste", "नमस्ते", "नमस्कार"),
    "home": ("Home", "डैशबोर्ड", "डॅशबोर्ड"),
    "chat": ("Chat", "चैट", "संवाद"),
    "disease": ("Disease Check", "रोग पहचान", "रोग निदान"),
    "mandi": ("Mandi Prices", "मंडी भाव", "बाजारभाव"),
    "profile": ("Profile", "प्रोफाइल", "प्रोफाइल"),
    "soon": ("Coming soon", "जल्द आ रहा है", "लवकरच येत आहे"),
    "newchat": ("New chat", "नई बातचीत", "नवीन संवाद"),
    "history": ("History", "पुरानी चैट", "इतिहास"),
    "ph": ("Type your question...", "सवाल पूछें...", "प्रश्न विचारा..."),
    "send": ("Send", "भेजें", "पाठवा"),
    "speak": ("🔊 Listen", "🔊 सुनें", "🔊 ऐका"),
    "offline": ("Internet needed", "इंटरनेट बंद है", "इंटरनेट बंद आहे"),
    "privacy": ("Privacy", "गोपनीयता", "गोपनीयता"),
    "del": ("Delete my account and data", "खाता हटाएं", "खाते नष्ट करा"),
    "delconf": ("All your data will be deleted permanently. Sure?", "क्या आप डेटा हटाना चाहते हैं?", "सर्व डेटा नष्ट करायचा का?"),
    "note": ("Free · No ads · Works on low internet", "मुफ्त · कोई विज्ञापन नहीं", "मोफत · जाहिरातमुक्त"),
    "askai": ("Ask AI", "AI से पूछें", "AI ला विचारा"),
    "mind": ("Mind Mitra", "माइंड मित्रा", "माइंड मित्रा"),
    "weather": ("Weather", "मौसम", "हवामान"),
    "wq1": ("When should I water my field?", "खेत में पानी कब दें?", "शेताला पाणी कधी द्यावे?"),
    "wq2": ("When should I sow soybean?", "सोयाबीन कब बोएं?", "सोयाबीन पेरणी कधी करावी?"),
    "wq3": ("Tell me about crop insurance", "फसल बीमा की जानकारी", "पीक विम्याबद्दल सांगा"),
    "empty": ("No chats yet", "कोई चैट नहीं", "जुने संभाषण नाही"),
    "c_soybean": ("Soybean", "सोयाबीन", "सोयाबीन"),
    "c_cotton": ("Cotton", "कपास", "कापूस"),
    "c_wheat": ("Wheat", "गेहूं", "गहू"),
    "c_rice": ("Rice", "चावल", "भात"),
    "c_maize": ("Maize", "मक्का", "मका"),
    "c_sugarcane": ("Sugarcane", "गन्ना", "ऊस"),
    "c_groundnut": ("Groundnut", "मूंगफली", "भुईमूग"),
    "c_pulses": ("Pulses", "दलहन", "कडधान्ये"),
    "c_vegetables": ("Vegetables", "सब्जियां", "भाजीपाला"),
    "c_fruits": ("Fruits", "फल", "फळबाग"),
    "c_spices": ("Spices", "मसाले", "मसाले"),
    "c_mustard": ("Mustard", "सरसों", "मोहरी"),
    "err_invalid_credentials": ("Wrong mobile or PIN", "गलत मोबाइल या पिन", "चुकीचा मोबाईल किंवा पिन"),
    "err_mobile_exists": ("This mobile number is already registered", "मोबाइल नंबर पहले से पंजीकृत है", "मोबाईल नंबर आधीच नोंदणीकृत आहे"),
    "err_rate_limited": ("Too many attempts, try again later", "कृपया प्रतीक्षा करें", "कृपया काही वेळ थांबा"),
    "err_llm_unavailable": ("AI cannot answer right now", "AI सर्वर व्यस्त है", "AI सर्व्हर व्यस्त आहे"),
    "err_not_logged_in": ("Please log in again", "कृपया पुनः लॉगिन करें", "कृपया पुन्हा लॉगिन करा"),
    "err_invalid": ("Some details are not valid", "जानकारी सही नहीं है", "माहिती योग्य नाही"),
    "err_generic": ("Something went wrong, try again", "कुछ गड़बड़ हुई", "काहीतरी चूक झाली"),
    "err_not_found": ("Not found", "रिकॉर्ड नहीं मिला", "आढळले नाही"),
    "hero_badge": ("FRESH FARMING TOWARD STEADY GROWTH", "सतत विकास और आधुनिक खेती की ओर", "शाश्वत शेती आणि समृद्धीचा मार्ग"),
    "hero_title": ("KrishiSaathi AI", "कृषि सार्थी AI", "कृषी सार्थी AI"),
    "hero_desc": ("Empowering Indian farmers with cutting-edge AI for crop health, fair mandi prices, zero-rejection PMFBY claims, debt relief, and wellness.", "फसल रोग पहचान, सही मंडी भाव, बिना रिजेक्शन फसल बीमा क्लेम, सस्ते KCC लोन और मानसिक संबल के लिए भारत का अग्रणी AI प्लेटफॉर्म।", "पिकावरील रोग निदान, अचूक बाजारभाव, विना-तक्रार पीक विमा (PMFBY), स्वस्त बँक कर्ज व शेतकरी मानसिक संबलासाठी संपूर्ण डिजिटल व्यासपीठ."),
    "get_started": ("GET STARTED", "शुरू करें", "सुरू करा"),
    "farms_supported": ("50K+ Farms supported", "50,000+ किसानों का विश्वास", "५०,०००+ शेतकरी बांधवांचा विश्वास"),
    "market_access": ("Market Access Support", "मंडी भाव व खरीदार समर्थन", "बाजारभाव व थेट विक्री"),
    "market_access_sub": ("Helping farmers reach wider buyers & best mandi rates.", "बिचौलियों से मुक्ति और नजदीकी मंडियों के उच्चतम दाम।", "दलालांशिवाय थेट नजीकच्या मंड्यांमधील सर्वोच्च दर मिळवा."),
    "realtime_analysis": ("Real-Time Analysis", "तत्काल फसल स्वास्थ्य जांच", "तातडीचे पीक आरोग्य निदान"),
    "realtime_analysis_sub": ("Instant crop health diagnostic & satellite weather boost.", "पत्ते का फोटो अपलोड कर तुरंत बीमारी का सटीक इलाज जानें।", "पानाचा फोटो काढून तत्काळ अचूक उपाय व फवारणी नियोजन जाणून घ्या."),
    "agri_supply": ("Agri-Supply Solutions", "असली खाद व बीज सत्यापन", "अस्सल बियाणे व औषध पडताळणी"),
    "agri_supply_sub": ("Authentic seeds, certified inputs & verified dealers.", "नकली कृषि उत्पादों की पहचान और अधिकृत डीलरों की सूची।", "बनावट कीटकनाशके ओळखा आणि अधिकृत विक्रेत्यांकडून खरेदी करा."),
    "product": ("Product Verify", "उत्पाद जांच", "खरे उत्पादन पडताळणी"),
    "insurance": ("Insurance Claim", "फसल बीमा (PMFBY)", "पीक विमा दावा (PMFBY)"),
    "loan": ("Loan Optimizer", "सस्ता लोन", "स्वस्त कर्ज शोध"),
    "advisor": ("Crop Advisor", "फसल सलाह", "पीक सल्ला"),
    "voice_diag": ("Voice Diagnosis", "बोलकर निदान", "आवाजाद्वारे निदान")
}

en_dict = {k: v[0] for k, v in sorted(base_keys.items())}
hi_dict = {k: v[1] for k, v in sorted(base_keys.items())}
mr_dict = {k: v[2] for k, v in sorted(base_keys.items())}

with open(os.path.join(i18n_dir, "en.json"), "w", encoding="utf-8") as f:
    json.dump(en_dict, f, ensure_ascii=False, indent=2)

with open(os.path.join(i18n_dir, "hi.json"), "w", encoding="utf-8") as f:
    json.dump(hi_dict, f, ensure_ascii=False, indent=2)

with open(os.path.join(i18n_dir, "mr.json"), "w", encoding="utf-8") as f:
    json.dump(mr_dict, f, ensure_ascii=False, indent=2)

print("Synchronized all 3 base language files with total keys:", len(base_keys))
