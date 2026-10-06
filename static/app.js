// KrishiSaathi AI - Progressive Web Application Frontend
// Features: Auth, 9 Farm Modules, Multilingual Voice, PDF Downloads, EcoFarm UI

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];

const SPEECH_LANGS = {
  hi: "hi-IN", mr: "mr-IN", en: "en-IN", pa: "pa-IN",
  gu: "gu-IN", ta: "ta-IN", te: "te-IN", kn: "kn-IN", bn: "bn-IN"
};

let I = {};
let me = null;
let currentChatId = null;
let isBusy = false;
let currentLang = localStorage.getItem("lang") || "en";
let currentTheme = localStorage.getItem("theme") || "light";

const t = k => I[k] || k;

// Toast Notification
function toast(msg, isBad = false) {
  const el = $("#toast");
  el.textContent = msg;
  el.className = "show" + (isBad ? " bad" : "");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => el.className = "", 3800);
}

// API Helper
async function api(path, method = "GET", body = null) {
  const opts = {
    method,
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" }
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  let data = null;
  try { data = await res.json(); } catch (_) {}
  if (!res.ok) {
    const errText = (data && data.detail) || "err_generic";
    throw new Error(errText);
  }
  return data;
}

const handleApiFail = err => {
  const key = "err_" + err.message;
  toast(I[key] || t("err_generic"), true);
};

// Theme Management
function applyTheme(themeName) {
  currentTheme = themeName;
  localStorage.setItem("theme", themeName);
  document.documentElement.setAttribute("data-theme", themeName);
  const isDark = themeName === "dark";
  const icon = $("#theme-icon");
  const text = $("#theme-text");
  if (icon) icon.textContent = isDark ? "☀️" : "🌙";
  if (text) text.textContent = isDark ? t("light") : t("dark");
}

// i18n Language Loader
async function setLanguage(l) {
  try {
    const res = await fetch(`/api/i18n/${l}`);
    if (!res.ok) throw new Error("lang_fail");
    I = await res.json();
  } catch (_) {
    toast("Language file load error", true);
    return;
  }
  currentLang = l;
  localStorage.setItem("lang", l);
  document.documentElement.lang = l;
  
  const landingSel = $("#landing-lang");
  const appSel = $("#app-lang");
  if (landingSel) landingSel.value = l;
  if (appSel) appSel.value = l;

  $$("[data-i18n]").forEach(el => {
    const k = el.dataset.i18n;
    if (I[k]) el.textContent = I[k];
  });

  const ci = $("#ci");
  if (ci) ci.placeholder = t("ph");
  applyTheme(currentTheme);
}

// Landing & Hero Transitions (Image 1 to Slide Login)
function initLandingHero() {
  const btnGetStarted = $("#btn-get-started");
  const btnNavLogin = $("#btn-nav-login");
  const btnBackHero = $("#btn-back-to-hero");
  const portal = $("#auth-slide-portal");
  const heroContent = $(".hero-content");

  function openPortal() {
    portal.style.display = "block";
    portal.scrollIntoView({ behavior: "smooth" });
  }

  function closePortal() {
    heroContent.scrollIntoView({ behavior: "smooth" });
    setTimeout(() => { portal.style.display = "none"; }, 500);
  }

  if (btnGetStarted) btnGetStarted.onclick = openPortal;
  if (btnNavLogin) btnNavLogin.onclick = openPortal;
  if (btnBackHero) btnBackHero.onclick = closePortal;

  // 1-Click Demo Login
  const btnDemo = $("#btn-fill-demo");
  if (btnDemo) {
    btnDemo.onclick = async () => {
      $("#fl").elements.mobile.value = "9876543210";
      $("#fl").elements.pin.value = "1234";
      try {
        const u = await api("/api/login", "POST", { mobile: "9876543210", pin: "1234" });
        await enterApp(u);
        toast(`Welcome ${u.name}!`);
      } catch (err) {
        handleApiFail(err);
      }
    };
  }
}

// App Entry & Exit
async function enterApp(user) {
  me = user;
  $("#landing-view").style.display = "none";
  $("#main-app").style.display = "block";
  
  // Set User Display
  const uDisp = $("#user-display-name");
  if (uDisp) uDisp.textContent = me.name;
  const wTitle = $("#welcome-banner-title");
  if (wTitle) wTitle.textContent = `${t("hello")} ${me.name}!`;
  $$(".user-name-inline").forEach(el => el.textContent = me.name);

  // Pre-fill Profile & Claim info
  if ($("#claim-name")) $("#claim-name").value = me.name;
  if ($("#claim-mobile")) $("#claim-mobile").value = "+91 " + me.mobile;
  if ($("#claim-district")) $("#claim-district").value = `${me.district}, ${me.state}`;
  if ($("#profile-mobile")) $("#profile-mobile").value = me.mobile;
  
  const pf = $("#pf");
  if (pf) {
    pf.elements.name.value = me.name;
    pf.elements.village.value = me.village || "";
    pf.elements.district.value = me.district || "";
    pf.elements.state.value = me.state || "";
    pf.elements.land.value = me.land || 0;
    if (me.crops) {
      pf.querySelectorAll('[name="crops"]').forEach(cb => {
        cb.checked = me.crops.includes(cb.value);
      });
    }
  }

  await setLanguage(me.language || currentLang);
  applyTheme(me.theme || currentTheme);

  // Initialize Default Modules
  loadFeatureTab("disease");
  initChatGreeting();
  loadMandiRates("Soybean");
  initLoanCalculator();
  loadWeatherForecast();
  loadClaimsList();
}

function leaveApp() {
  me = null;
  currentChatId = null;
  $("#msgs").replaceChildren();
  $("#main-app").style.display = "none";
  $("#landing-view").style.display = "flex";
  $("#auth-slide-portal").style.display = "none";
}

// Tab Switching
function loadFeatureTab(tabName) {
  $$(".tab-pill").forEach(p => p.classList.toggle("active", p.dataset.tab === tabName));
  const panels = [
    "disease", "insurance", "loan", "mandi", "product",
    "advisor", "weather", "voice", "mind", "profile"
  ];
  panels.forEach(p => {
    const el = $(`#panel-${p}`);
    if (el) el.style.display = p === tabName ? "block" : "none";
  });
}

// ==========================================================
// FEATURE 1: 📸 CROP DISEASE DETECTION
// ==========================================================
function initDiseaseModule() {
  let selectedLeafSample = "soybean_mosaic";

  $$(".sample-item").forEach(item => {
    item.onclick = () => {
      $$(".sample-item").forEach(i => i.classList.remove("selected"));
      item.classList.add("selected");
      selectedLeafSample = item.dataset.leaf;
    };
  });

  const btnRun = $("#btn-run-diagnosis");
  let lastDiagnosisData = null;

  if (btnRun) {
    btnRun.onclick = async () => {
      btnRun.textContent = "Analyzing Leaf Texture...";
      try {
        const res = await api("/api/disease-check", "POST", { sample_key: selectedLeafSample, crop: "Soybean" });
        lastDiagnosisData = res;
        
        $("#diag-disease-name").textContent = res.disease;
        $("#diag-confidence").textContent = `${res.confidence}%`;
        const sevEl = $("#diag-severity");
        sevEl.textContent = res.severity;
        sevEl.className = "badge-severity " + (res.severity === "High" ? "badge-high" : res.severity === "Medium" ? "badge-medium" : "badge-low");
        $("#diag-cost").textContent = res.cost;

        const symList = $("#diag-symptoms");
        symList.replaceChildren();
        res.symptoms.forEach(s => {
          const li = document.createElement("li");
          li.textContent = s;
          symList.appendChild(li);
        });

        $("#diag-treatment").textContent = res.treatment;
        $("#diag-prevention").textContent = res.prevention;
        $("#disease-result-container").style.display = "block";
        $("#disease-result-container").scrollIntoView({ behavior: "smooth" });
      } catch (err) {
        handleApiFail(err);
      } finally {
        btnRun.textContent = "🔍 Analyze Crop Health";
      }
    };
  }

  // Download PDF
  const btnPdf = $("#btn-download-disease-pdf");
  if (btnPdf) {
    btnPdf.onclick = async () => {
      if (!lastDiagnosisData) return;
      try {
        const res = await fetch("/api/disease/pdf", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(lastDiagnosisData)
        });
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `KrishiSaathi_Disease_${lastDiagnosisData.disease.replace(/\s+/g, '_')}.pdf`;
        a.click();
        toast("Diagnostic PDF Downloaded!");
      } catch (_) {
        toast("Failed to download PDF", true);
      }
    };
  }

  // WhatsApp Share
  const btnWa = $("#btn-share-whatsapp");
  if (btnWa) {
    btnWa.onclick = () => {
      if (!lastDiagnosisData) return;
      const text = `🌾 *KrishiSaathi AI Crop Diagnosis*\n*Disease:* ${lastDiagnosisData.disease} (${lastDiagnosisData.confidence}% Confidence)\n*Severity:* ${lastDiagnosisData.severity}\n*Estimated Cost:* ${lastDiagnosisData.cost}\n*Treatment:* ${lastDiagnosisData.treatment}`;
      window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, "_blank");
    };
  }
}

// ==========================================================
// FEATURE 2: 🏥 PMFBY INSURANCE CLAIM AUTO-FILL WIZARD
// ==========================================================
function initInsuranceModule() {
  $$(".wizard-step-node").forEach(node => {
    node.onclick = () => {
      const step = node.dataset.step;
      setWizardStep(parseInt(step));
    };
  });

  $$(".next-step").forEach(btn => {
    btn.onclick = () => setWizardStep(parseInt(btn.dataset.to));
  });

  $$(".prev-step").forEach(btn => {
    btn.onclick = () => setWizardStep(parseInt(btn.dataset.to));
  });

  function setWizardStep(s) {
    $$(".wizard-step-node").forEach(n => {
      const st = parseInt(n.dataset.step);
      n.classList.toggle("active", st === s);
      n.classList.toggle("done", st < s);
    });
    $$(".wizard-step-panel").forEach(p => p.style.display = "none");
    const activePanel = $(`#wstep-${s}`);
    if (activePanel) activePanel.style.display = "block";
  }

  // Submit Claim
  const btnSubmit = $("#btn-submit-pmfby");
  if (btnSubmit) {
    btnSubmit.onclick = async () => {
      btnSubmit.textContent = "Transmitting to PMFBY Portal...";
      const crop = $("#claim-crop").value;
      const survey = $("#claim-survey").value;
      const acres = parseFloat($("#claim-acres").value) || 1.0;
      const cause = $("#claim-cause").value;
      const pct = parseInt($("#claim-pct").value) || 50;

      try {
        const res = await api("/api/claims", "POST", {
          crop, survey_number: survey, land_acres: acres, loss_cause: cause, loss_percentage: pct
        });
        $("#submitted-claim-id").textContent = res.claim_id;
        $("#submitted-claim-payout").textContent = `₹${res.estimated_payout.toLocaleString()}`;
        setWizardStep(5);
        toast("PMFBY Claim Submitted Successfully!");
        loadClaimsList();
      } catch (err) {
        handleApiFail(err);
      } finally {
        btnSubmit.textContent = "🚀 Submit Claim to National PMFBY Portal";
      }
    };
  }

  // Download Receipt PDF
  const btnDlReceipt = $("#btn-download-claim-receipt");
  if (btnDlReceipt) {
    btnDlReceipt.onclick = () => {
      const cid = $("#submitted-claim-id").textContent;
      window.open(`/api/claims/${cid}/pdf`, "_blank");
    };
  }
}

async function loadClaimsList() {
  const container = $("#claims-history-list");
  if (!container) return;
  try {
    const claims = await api("/api/claims");
    if (!claims.length) {
      container.textContent = "No claims filed yet. Fill form above to submit your first claim.";
      return;
    }
    container.innerHTML = claims.map(c => `
      <div style="background:var(--surface-alt); padding:12px; border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <b>${c.claim_id}</b> (${c.crop} - ${c.land_acres} Acres)
          <div style="font-size:0.8rem; color:var(--text-muted);">${c.loss_cause} · Damage: ${c.loss_percentage}% · Date: ${c.date}</div>
        </div>
        <div style="text-align:right;">
          <b style="color:var(--primary);">₹${c.estimated_payout.toLocaleString()}</b>
          <div style="margin-top:4px;"><a href="/api/claims/${c.claim_id}/pdf" target="_blank" style="font-size:0.8rem; font-weight:700;">📥 Receipt PDF</a></div>
        </div>
      </div>
    `).join("");
  } catch (_) {}
}

// ==========================================================
// FEATURE 3: 💸 LOAN OPTIMIZER
// ==========================================================
function initLoanCalculator() {
  const sliderAmount = $("#loan-slider-amount");
  const sliderTenure = $("#loan-slider-tenure");

  async function updateLoanComparison() {
    const P = parseFloat(sliderAmount.value);
    const N = parseInt(sliderTenure.value);
    $("#loan-amount-val").textContent = `₹${P.toLocaleString()}`;
    $("#loan-tenure-val").textContent = `${N} Year${N > 1 ? 's' : ''}`;

    try {
      const data = await api("/api/loans/calculate", "POST", { principal: P, tenure_years: N });
      const container = $("#loan-comparison-cards");
      if (!container) return;
      container.innerHTML = data.schemes.map(s => {
        const isDanger = s.annual_rate >= 24;
        const isKcc = s.annual_rate <= 5;
        return `
          <div style="background:var(--surface); border:1px solid ${isDanger ? 'var(--error)' : isKcc ? 'var(--primary)' : 'var(--border)'}; border-radius:var(--radius-md); padding:16px; box-shadow:var(--shadow-sm);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
              <div>
                <b style="font-size:1.1rem; color:${isDanger ? 'var(--error)' : 'var(--text-main)'};">${s.name}</b>
                <div style="font-size:0.82rem; color:var(--text-muted);">${s.type} · ${s.interest_subsidy}</div>
              </div>
              <div style="text-align:right;">
                <b style="font-size:1.3rem; color:${isDanger ? 'var(--error)' : 'var(--primary)'};">${s.annual_rate}% p.a.</b>
              </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; font-size:0.88rem; background:var(--surface-alt); padding:10px; border-radius:6px; margin:10px 0;">
              <div>Monthly EMI: <b>₹${s.monthly_emi.toLocaleString()}</b></div>
              <div>Total Interest: <b>₹${s.total_interest.toLocaleString()}</b></div>
              <div>Total Payable: <b>₹${s.total_repayable.toLocaleString()}</b></div>
            </div>
            ${!isDanger ? `
              <div style="font-size:0.85rem; color:var(--primary); font-weight:700;">
                💰 Money Saved vs Informal Moneylender: ₹${s.saved_vs_moneylender.toLocaleString()}!
              </div>
            ` : `
              <div style="font-size:0.82rem; color:var(--error); font-weight:700;">
                ⚠️ WARNING: Compound interest traps farmers in generational poverty. Never take unsecured loans from local lenders!
              </div>
            `}
          </div>
        `;
      }).join("");
    } catch (_) {}
  }

  if (sliderAmount) sliderAmount.oninput = updateLoanComparison;
  if (sliderTenure) sliderTenure.oninput = updateLoanComparison;
  if (sliderAmount) updateLoanComparison();
}

// ==========================================================
// FEATURE 4: 🏪 MANDI PRICES DISCOVERY
// ==========================================================
async function loadMandiRates(crop = "Soybean") {
  $$(".mandi-crop-filter").forEach(b => b.classList.toggle("active", b.dataset.crop === crop));
  try {
    const res = await api(`/api/mandi-prices?crop=${encodeURIComponent(crop)}`);
    const tBody = $("#mandi-table-body");
    if (!tBody) return;
    tBody.innerHTML = res.mandis.map(m => `
      <tr style="border-bottom:1px solid var(--border);">
        <td style="padding:10px; font-weight:600;">${m.mandi}</td>
        <td style="padding:10px; color:var(--text-muted);">${m.district}</td>
        <td style="padding:10px;">${m.distance_km} km</td>
        <td style="padding:10px; font-weight:800; color:var(--primary); font-size:1.05rem;">₹${m.modal_price.toLocaleString()}</td>
        <td style="padding:10px; font-size:0.82rem; color:var(--text-muted);">₹${m.min_price} - ₹${m.max_price}</td>
        <td style="padding:10px; font-weight:700; color:${m.trend_pct >= 0 ? 'var(--primary)' : 'var(--error)'};">
          ${m.trend_pct >= 0 ? '▲ +' : '▼ '}${m.trend_pct}%
        </td>
      </tr>
    `).join("");

    if (res.recommendation && $("#mandi-recommendation-text")) {
      $("#mandi-recommendation-text").textContent = res.recommendation.verdict;
    }
  } catch (_) {}
}

function initMandiModule() {
  $$(".mandi-crop-filter").forEach(b => {
    b.onclick = () => loadMandiRates(b.dataset.crop);
  });
}

// ==========================================================
// FEATURE 5: 🌱 PRODUCT VERIFY (FAKE DETECTION)
// ==========================================================
function initProductModule() {
  $$(".demo-batch-btn").forEach(btn => {
    btn.onclick = () => {
      $("#pv-batch").value = btn.dataset.batch;
      $("#pv-company").value = btn.dataset.comp;
      $("#pv-prod").value = btn.dataset.prod;
      verifyProductAction();
    };
  });

  const btnVerify = $("#btn-verify-product");
  let lastProductVerdict = null;

  async function verifyProductAction() {
    const batch = $("#pv-batch").value.trim();
    const company = $("#pv-company").value.trim();
    const prod = $("#pv-prod").value.trim();
    if (!batch || !company) return toast("Enter batch and manufacturer", true);

    btnVerify.textContent = "Verifying Batch...";
    try {
      const res = await api("/api/product-verify", "POST", { batch_no: batch, company, product_name: prod });
      lastProductVerdict = res;
      const box = $("#pv-result-box");
      const isFake = res.status.includes("Fake");
      const isGenuine = res.status.includes("Genuine");

      box.style.display = "block";
      box.style.borderLeftColor = isFake ? "var(--error)" : isGenuine ? "var(--primary)" : "var(--secondary)";
      box.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <h4 style="font-size:1.3rem; color:${isFake ? 'var(--error)' : isGenuine ? 'var(--primary-dark)' : '#B78103'};">${res.status} (${res.confidence}% Match)</h4>
          <span style="font-size:0.85rem; color:var(--text-muted);">Batch: <b>${res.batch_no}</b></span>
        </div>
        <p style="font-size:0.9rem; margin-bottom:8px;"><b>Community Reports:</b> ${res.community_feedback}</p>
        <p style="font-size:0.9rem; margin-bottom:12px;"><b>Action Advice:</b> ${res.action}</p>

        ${isFake ? `
          <button id="btn-download-complaint-pdf" class="btn-auth-primary" style="width:auto; padding:8px 20px; background:var(--error); margin-bottom:12px;">
            ⚠️ Auto-Generate Complaint PDF to District Agri Officer
          </button>
        ` : ''}

        ${res.nearest_dealers && res.nearest_dealers.length ? `
          <div style="font-size:0.88rem; margin-top:10px;">
            <b>Authorized Dealers in District:</b>
            <ul style="padding-left:20px; margin-top:4px;">
              ${res.nearest_dealers.map(d => `<li>${d.name} (${d.dist}) · Ph: ${d.phone}</li>`).join("")}
            </ul>
          </div>
        ` : ''}
      `;

      const btnCompPdf = $("#btn-download-complaint-pdf");
      if (btnCompPdf) {
        btnCompPdf.onclick = async () => {
          try {
            const pdfRes = await fetch("/api/product/complaint-pdf", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(lastProductVerdict)
            });
            const blob = await pdfRes.blob();
            const a = document.createElement("a");
            a.href = window.URL.createObjectURL(blob);
            a.download = `Complaint_Counterfeit_${lastProductVerdict.batch_no}.pdf`;
            a.click();
            toast("Official Complaint Letter Downloaded!");
          } catch (_) {
            toast("Failed to download complaint PDF", true);
          }
        };
      }
    } catch (err) {
      handleApiFail(err);
    } finally {
      btnVerify.textContent = "🔍 Check Authenticity";
    }
  }

  if (btnVerify) btnVerify.onclick = verifyProductAction;
}

// ==========================================================
// FEATURE 6: 🌾 CROP ADVISOR
// ==========================================================
function initAdvisorModule() {
  const btnCalc = $("#btn-calc-advisor");
  if (btnCalc) {
    btnCalc.onclick = async () => {
      const crop = $("#adv-crop").value;
      const soil = $("#adv-soil").value;
      const acres = parseFloat($("#adv-acres").value) || 2.0;

      try {
        const res = await api("/api/crop-advisor", "POST", { crop, soil_type: soil, acres });
        const box = $("#adv-result-box");
        box.innerHTML = `
          <div class="result-card" style="margin-bottom:16px;">
            <h4 style="color:var(--primary-dark); margin-bottom:10px;">🧪 Scientific Fertilizer Schedule (${crop} - ${acres} Acres)</h4>
            <div style="display:flex; flex-direction:column; gap:8px;">
              ${res.fertilizer_schedule.map(f => `
                <div style="background:var(--surface); padding:10px; border-radius:6px; border:1px solid var(--border);">
                  <b>${f.stage}:</b>
                  <div style="color:var(--primary); font-weight:600; margin-top:2px;">${f.fertilizer}</div>
                  <div style="font-size:0.8rem; color:var(--text-muted);">${f.purpose}</div>
                </div>
              `).join("")}
            </div>
          </div>

          <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
            <div class="result-card">
              <h4 style="color:var(--accent); margin-bottom:6px;">💧 Irrigation Management</h4>
              <ul style="padding-left:18px; font-size:0.85rem;">
                ${res.irrigation_plan.map(i => `<li><b>${i.phase}:</b> ${i.frequency}</li>`).join("")}
              </ul>
            </div>
            <div class="result-card" style="border-left-color:var(--lime);">
              <h4 style="color:var(--primary-dark); margin-bottom:6px;">💰 Projected Economics (${acres} Acres)</h4>
              <div style="font-size:0.88rem;">
                <div>Estimated Total Harvest: <b>${res.economics.expected_yield_total}</b></div>
                <div>Gross Revenue: <b>₹${res.economics.estimated_gross_revenue.toLocaleString()}</b></div>
                <div>Production Cost: <b>₹${res.economics.estimated_production_cost.toLocaleString()}</b></div>
                <div style="color:var(--primary); font-weight:800; font-size:1.1rem; margin-top:6px;">
                  Net Projected Profit: ₹${res.economics.estimated_net_profit.toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        `;
      } catch (err) {
        handleApiFail(err);
      }
    };
  }
}

// ==========================================================
// FEATURE 7: 🌦️ WEATHER ADVISORY
// ==========================================================
async function loadWeatherForecast() {
  try {
    const res = await api("/api/weather?district=Nashik&state=Maharashtra");
    const grid = $("#weather-forecast-grid");
    if (!grid) return;
    grid.innerHTML = res.forecast.map(f => `
      <div style="background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-sm); padding:12px; text-align:center;">
        <b style="font-size:0.95rem;">${f.day}</b>
        <div style="font-size:0.75rem; color:var(--text-muted);">${f.date}</div>
        <div style="font-size:1.6rem; margin:6px 0;">${f.condition.split(" ")[1] || '⛅'}</div>
        <div style="font-weight:700; font-size:0.95rem;">${f.temp_max}° / ${f.temp_min}°C</div>
        <div style="font-size:0.8rem; color:${f.rain_prob > 50 ? 'var(--accent)' : 'var(--text-muted)'}; margin-top:4px;">
          🌧️ ${f.rain_prob}% (${f.rain_mm}mm)
        </div>
      </div>
    `).join("");
  } catch (_) {}
}

// ==========================================================
// FEATURE 8: 🗣️ VOICE DIAGNOSIS & INTERACTION
// ==========================================================
function initVoiceModule() {
  const btnBigMic = $("#btn-voice-record-big");
  const statusEl = $("#voice-record-status");
  const outputEl = $("#voice-diag-output");

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SR) {
    if (statusEl) statusEl.textContent = "Speech recognition supported in Chrome/Edge browsers.";
    return;
  }

  const recognizer = new SR();
  recognizer.continuous = false;
  recognizer.interimResults = false;

  if (btnBigMic) {
    btnBigMic.onclick = () => {
      recognizer.lang = SPEECH_LANGS[currentLang] || "hi-IN";
      btnBigMic.style.background = "var(--error)";
      statusEl.textContent = "Listening... Please speak symptoms clearly.";
      try {
        recognizer.start();
      } catch (_) {}
    };
  }

  recognizer.onresult = async event => {
    btnBigMic.style.background = "var(--primary)";
    const spokenText = event.results[0][0].transcript;
    statusEl.textContent = `You said: "${spokenText}"`;

    try {
      const res = await api("/api/voice-diagnose", "POST", { transcript: spokenText });
      outputEl.style.display = "block";
      outputEl.innerHTML = `
        <h4 style="color:var(--primary-dark); font-size:1.2rem;">Diagnosis: ${res.suspected_disease || 'Symptom Check'}</h4>
        <p style="font-size:0.9rem; margin:6px 0;"><b>Detected Symptom:</b> ${res.symptom_detected}</p>
        <p style="font-size:0.9rem; margin:6px 0;"><b>Immediate Action:</b> ${res.immediate_action}</p>
        <button id="btn-replay-audio" class="btn-auth-primary" style="width:auto; padding:6px 18px; margin-top:8px;">
          🔊 Replay Voice Answer
        </button>
      `;

      speakUtterance(res.audio_summary || res.immediate_action);

      const btnReplay = $("#btn-replay-audio");
      if (btnReplay) btnReplay.onclick = () => speakUtterance(res.audio_summary || res.immediate_action);
    } catch (err) {
      handleApiFail(err);
    }
  };

  recognizer.onerror = () => {
    btnBigMic.style.background = "var(--primary)";
    statusEl.textContent = "Could not hear clearly. Please tap to try again.";
  };
}

function speakUtterance(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = SPEECH_LANGS[currentLang] || "hi-IN";
  u.rate = 0.95;
  window.speechSynthesis.speak(u);
}

// ==========================================================
// FEATURE 9: 😔 MIND MITRA (MENTAL HEALTH & COUNSELING)
// ==========================================================
function initMindMitra() {
  $$(".mood-btn").forEach(btn => {
    btn.onclick = async () => {
      const mood = btn.dataset.mood;
      const score = parseInt(btn.dataset.score);
      try {
        const res = await api("/api/mood", "POST", { mood, score, category: "Farm Stress", note: "Logged from Mind Mitra" });
        toast(res.comfort_message);
      } catch (err) {
        handleApiFail(err);
      }
    };
  });
}

// ==========================================================
// RIGHT COLUMN: ALWAYS AVAILABLE AI CHATBOT
// ==========================================================
function initChatbot() {
  const msgsContainer = $("#msgs");
  const form = $("#cf");
  const ci = $("#ci");
  const btnNewChat = $("#btn-new-chat");
  const btnToggleHist = $("#btn-toggle-hist");
  const histDrawer = $("#chat-hist-drawer");
  const btnMic = $("#btn-chat-mic");

  function appendMessage(role, text) {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role}`;
    bubble.textContent = text;

    if (role === "assistant" && window.speechSynthesis) {
      const btnSpeak = document.createElement("button");
      btnSpeak.className = "btn-speak-msg";
      btnSpeak.innerHTML = "🔊 <span>Listen</span>";
      btnSpeak.onclick = () => speakUtterance(text);
      bubble.appendChild(btnSpeak);
    }

    msgsContainer.appendChild(bubble);
    bubble.scrollIntoView({ behavior: "smooth", block: "end" });
    return bubble;
  }

  async function sendMessage(text) {
    text = text.trim();
    if (!text || isBusy) return;
    if (!navigator.onLine) return toast(t("offline"), true);

    isBusy = true;
    appendMessage("user", text);
    ci.value = "";
    const waiting = appendMessage("assistant", "Thinking...");

    try {
      const res = await api("/api/chat", "POST", { message: text, chat_id: currentChatId });
      currentChatId = res.chat_id;
      waiting.remove();
      appendMessage("assistant", res.reply);
      if (me && me.voice) speakUtterance(res.reply);
    } catch (err) {
      waiting.remove();
      handleApiFail(err);
    } finally {
      isBusy = false;
    }
  }

  if (form) {
    form.onsubmit = e => {
      e.preventDefault();
      sendMessage(ci.value);
    };
  }

  // Suggestion Chips (Prompt requirement!)
  $$(".chip-btn").forEach(chip => {
    chip.onclick = () => sendMessage(chip.dataset.query);
  });

  if (btnNewChat) {
    btnNewChat.onclick = () => {
      currentChatId = null;
      msgsContainer.replaceChildren();
      initChatGreeting();
    };
  }

  if (btnToggleHist) {
    btnToggleHist.onclick = async () => {
      const isHidden = histDrawer.style.display === "none";
      histDrawer.style.display = isHidden ? "block" : "none";
      if (isHidden) {
        try {
          const chats = await api("/api/chats");
          if (!chats.length) {
            histDrawer.textContent = "No past chats yet.";
            return;
          }
          histDrawer.innerHTML = chats.map(c => `
            <button class="hist-item-btn" data-cid="${c.id}">${c.title} (${c.created_at})</button>
          `).join("");
          $$(".hist-item-btn").forEach(b => {
            b.onclick = async () => {
              const cid = parseInt(b.dataset.cid);
              currentChatId = cid;
              const ms = await api(`/api/chats/${cid}`);
              msgsContainer.replaceChildren();
              ms.forEach(m => appendMessage(m.role, m.content));
              histDrawer.style.display = "none";
            };
          });
        } catch (_) {}
      }
    };
  }

  // Voice Input (Web Speech Recognition)
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SR && btnMic) {
    const recog = new SR();
    recog.continuous = false;
    btnMic.onclick = () => {
      recog.lang = SPEECH_LANGS[currentLang] || "hi-IN";
      btnMic.classList.add("recording");
      try { recog.start(); } catch (_) {}
    };
    recog.onresult = e => {
      btnMic.classList.remove("recording");
      const transcript = e.results[0][0].transcript;
      ci.value = transcript;
      sendMessage(transcript);
    };
    recog.onerror = () => btnMic.classList.remove("recording");
    recog.onend = () => btnMic.classList.remove("recording");
  }
}

function initChatGreeting() {
  const msgsContainer = $("#msgs");
  if (!msgsContainer || msgsContainer.children.length) return;
  const name = me ? me.name : "Kisan Mitra";
  const bubble = document.createElement("div");
  bubble.className = "chat-bubble assistant";
  bubble.textContent = `Namaste ${name}! I am your KrishiSaathi AI farming assistant. How can I assist you with crop health, PMFBY claims, loans, or mandi rates today?`;
  msgsContainer.appendChild(bubble);
}

// Profile & Account Management
function initProfileModule() {
  const pf = $("#pf");
  if (pf) {
    pf.onsubmit = async e => {
      e.preventDefault();
      const cropsChecked = [...pf.querySelectorAll('[name="crops"]:checked')].map(c => c.value);
      const payload = {
        name: pf.elements.name.value.trim(),
        village: pf.elements.village.value.trim(),
        district: pf.elements.district.value.trim(),
        state: pf.elements.state.value.trim(),
        land: parseFloat(pf.elements.land.value) || 0,
        crops: cropsChecked,
        language: currentLang,
        voice: me ? me.voice : false,
        theme: currentTheme
      };
      const pinVal = pf.elements.pin.value.trim();
      if (pinVal) payload.new_pin = pinVal;

      try {
        me = await api("/api/me", "PUT", payload);
        toast("Profile & farm records saved!");
        const uDisp = $("#user-display-name");
        if (uDisp) uDisp.textContent = me.name;
      } catch (err) {
        handleApiFail(err);
      }
    };
  }

  const btnDel = $("#btn-del-account");
  if (btnDel) {
    btnDel.onclick = async () => {
      if (!confirm("Are you sure? All farm data, claims, and chat history will be permanently deleted.")) return;
      try {
        await api("/api/me", "DELETE");
        toast("Account deleted");
        leaveApp();
      } catch (err) {
        handleApiFail(err);
      }
    };
  }

  const btnLogout = $("#btn-logout");
  if (btnLogout) {
    btnLogout.onclick = async () => {
      try { await api("/api/logout", "POST"); } catch (_) {}
      leaveApp();
    };
  }
}

// Global Initialization
window.addEventListener("DOMContentLoaded", async () => {
  applyTheme(currentTheme);
  await setLanguage(currentLang);

  initLandingHero();
  initDiseaseModule();
  initInsuranceModule();
  initLoanCalculator();
  initMandiModule();
  initProductModule();
  initAdvisorModule();
  initVoiceModule();
  initMindMitra();
  initChatbot();
  initProfileModule();

  // Navigation tab listeners
  $$(".tab-pill").forEach(p => {
    p.addEventListener("click", () => {
      if (p.dataset.tab) loadFeatureTab(p.dataset.tab);
    });
  });

  // Theme toggle listener
  const themeToggle = $("#theme-toggle");
  if (themeToggle) {
    themeToggle.onclick = () => {
      const next = currentTheme === "dark" ? "light" : "dark";
      applyTheme(next);
      if (me) {
        api("/api/me", "PUT", { ...me, theme: next }).catch(() => {});
      }
    };
  }

  // Language dropdown listeners
  const landingLang = $("#landing-lang");
  if (landingLang) {
    landingLang.onchange = e => setLanguage(e.target.value);
  }
  const appLang = $("#app-lang");
  if (appLang) {
    appLang.onchange = e => {
      setLanguage(e.target.value);
      if (me) {
        api("/api/me", "PUT", { ...me, language: e.target.value }).catch(() => {});
      }
    };
  }

  // Login form submission
  const fl = $("#fl");
  if (fl) {
    fl.onsubmit = async e => {
      e.preventDefault();
      const mobile = fl.elements.mobile.value.trim();
      const pin = fl.elements.pin.value.trim();
      try {
        const u = await api("/api/login", "POST", { mobile, pin });
        await enterApp(u);
        toast(`Welcome back, ${u.name}!`);
      } catch (err) {
        handleApiFail(err);
      }
    };
  }

  // Signup form submission
  const fs = $("#fs");
  if (fs) {
    fs.onsubmit = async e => {
      e.preventDefault();
      const payload = {
        name: fs.elements.name.value.trim(),
        mobile: fs.elements.mobile.value.trim(),
        village: fs.elements.village.value.trim(),
        district: fs.elements.district.value,
        state: fs.elements.state.value,
        land: parseFloat(fs.elements.land.value) || 0,
        crops: ["soybean", "wheat"],
        pin: fs.elements.pin.value.trim(),
        language: currentLang,
        voice: false,
        theme: currentTheme
      };
      try {
        const u = await api("/api/signup", "POST", payload);
        await enterApp(u);
        toast(`Account created! Welcome ${u.name}!`);
      } catch (err) {
        handleApiFail(err);
      }
    };
  }

  // Check if session cookie exists
  try {
    const user = await api("/api/me");
    if (user && user.id) {
      await enterApp(user);
    }
  } catch (_) {
    // Show landing
  }

  // Service Worker for PWA
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  }
});
