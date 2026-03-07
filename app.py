"""
app.py  —  AI Sales Proposal Generator + CRM Auto-Updater

"""

import os
import csv
import io
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── CRM Helpers ───────────────────────────────────────────────────────────────
def _build_crm_entry(proposal: dict, client_data: dict) -> dict:
    company  = client_data.get("company_name", "")
    industry = client_data.get("industry", "")
    budget   = f"${client_data.get('budget_min',0):,} – ${client_data.get('budget_max',0):,}"
    email_raw = proposal.get("_followup_email", "")
    subject   = next(
        (l.split(":", 1)[1].strip() for l in email_raw.split("\n")
         if l.lower().startswith("subject:")), ""
    )
    inv = proposal.get("total_investment",
          int((client_data.get("budget_min", 0) + client_data.get("budget_max", 0)) / 2))
    return {
        "lead_info": {
            "name":            company,
            "industry":        industry,
            "estimated_value": budget,
            "budget_num":      inv,
            "status":          "Proposal Sent",
            "added_at":        datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "proposal_metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "summary":      proposal.get("executive_summary", "")[:200] + "...",
            "roi":          proposal.get("roi_percentage", 0),
            "payback":      proposal.get("payback_period_months", "N/A"),
        },
        "follow_up_email": {
            "subject": subject,
            "body":    email_raw,
            "status":  "Draft — Not Sent",
        },
        "deal": {
            "stage":          "Proposal Sent",
            "probability":    55,
            "weighted_value": int(inv * 0.55),
            "next_action":    "Follow-up in 3 days",
        },
    }

def _entries_to_csv(entries: list) -> bytes:
    if not entries:
        return b""
    buf    = io.StringIO()
    fields = ["Name","Industry","Budget","Est. Value","Status","Stage",
              "Probability","Weighted Value","ROI %","Payback","Email Subject","Added At","Summary"]
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    for e in entries:
        li   = e.get("lead_info", {})
        deal = e.get("deal", {})
        meta = e.get("proposal_metadata", {})
        fu   = e.get("follow_up_email", {})
        w.writerow({
            "Name":           li.get("name",""),
            "Industry":       li.get("industry",""),
            "Budget":         li.get("estimated_value",""),
            "Est. Value":     li.get("budget_num", 0),
            "Status":         li.get("status",""),
            "Stage":          deal.get("stage",""),
            "Probability":    deal.get("probability",""),
            "Weighted Value": deal.get("weighted_value",""),
            "ROI %":          meta.get("roi",""),
            "Payback":        meta.get("payback",""),
            "Email Subject":  fu.get("subject","") if isinstance(fu, dict) else "",
            "Added At":       li.get("added_at",""),
            "Summary":        meta.get("summary",""),
        })
    return buf.getvalue().encode()

def _load_crm(path="crm_data.json") -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _save_crm(entries: list, path="crm_data.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Sales Proposal Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --bg:#0A0E1A; --surface:#111827; --border:#1F2A3C;
  --accent:#5C00D4; --accent2:#3B82F6; --warn:#F59E0B; --danger:#EF4444;
  --text:#E2E8F0; --muted:#F5F5F5; --card:#151D2E;
}
html,body,[class*="css"]{font-family:'Space Grotesk',sans-serif;background:var(--bg)!important;color:var(--text)!important;}

.hackathon-banner{background:linear-gradient(135deg,#0A0E1A 0%,#0F1F3D 50%,#0A1628 100%);border:1px solid var(--border);border-top:3px solid var(--accent);border-radius:16px;padding:2rem 2.5rem;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:space-between;gap:2rem;position:relative;overflow:hidden;}
.hackathon-banner::before{content:'';position:absolute;top:-60px;right:-60px;width:200px;height:300px;background:radial-gradient(circle,rgba(0,212,170,0.08) 0%,transparent 70%);border-radius:50%;}
.banner-tag{display:inline-flex;align-items:center;gap:.4rem;background:rgba(0,212,170,0.12);color:var(--accent);border:1px solid rgba(0,212,170,0.25);border-radius:20px;padding:.25rem .85rem;font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.75rem;}
.banner-title{font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#fff;line-height:1.5;margin:0 0 .5rem;}
.banner-title span{color:var(--accent);}
.banner-sub{font-size:.88rem;color:var(--muted);line-height:1.5;max-width:520px;}
.bstat{text-align:center;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:10px;padding:.6rem 1rem;min-width:80px;}
.bstat-val{font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:var(--accent);}
.bstat-lbl{font-size:.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-top:.15rem;}

.workflow-row{display:flex;align-items:center;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem 1.5rem;margin-bottom:1.5rem;overflow-x:auto;}
.wf-step{display:flex;align-items:center;gap:.6rem;flex:1;min-width:120px;padding:.4rem .6rem;border-radius:8px;}
.wf-step.active{background:rgba(0,212,170,0.1);}
.wf-step.done{background:rgba(0,212,170,0.06);}
.wf-icon{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.9rem;background:var(--border);border:2px solid var(--border);flex-shrink:0;}
.wf-step.active .wf-icon,.wf-step.done .wf-icon{background:rgba(0,212,170,0.15);border-color:var(--accent);}
.wf-label{font-size:.75rem;font-weight:600;color:var(--muted);line-height:1.3;}
.wf-step.active .wf-label,.wf-step.done .wf-label{color:var(--text);}
.wf-arrow{color:var(--border);font-size:1.9rem;margin:0 .2rem;flex-shrink:0;}

.sec-label{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--accent);margin:.75rem 0 .5rem;display:flex;align-items:center;gap:.5rem;}
.sec-label::after{content:'';flex:1;height:2px;background:var(--border);}

.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem;margin-bottom:1.25rem;}
.kpi-box{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.1rem 1rem;position:relative;overflow:hidden;}
.kpi-box::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
.kpi-green::before{background:var(--accent);}
.kpi-blue::before{background:var(--accent2);}
.kpi-amber::before{background:var(--warn);}
.kpi-val{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#fff;line-height:1;}
.kpi-lbl{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-top:.3rem;}
.kpi-sub{font-size:.75rem;margin-top:.2rem;}
.kpi-green .kpi-sub{color:var(--accent);}
.kpi-blue .kpi-sub{color:var(--accent2);}
.kpi-amber .kpi-sub{color:var(--warn);}

.output-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.4rem 1.5rem;margin-bottom:1rem;line-height:1.75;color:var(--text);font-size:.92rem;}
.challenge-pill{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);border-left:3px solid var(--danger);border-radius:8px;padding:.55rem .9rem;margin:.35rem 0;font-size:.88rem;color:#FCA5A5;}
.email-output{background:#0D1520;border:1px solid var(--border);border-left:3px solid var(--accent2);border-radius:10px;padding:1.2rem 1.4rem;font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.85;color:#CBD5E1;white-space:pre-wrap;}
.rag-card{background:rgba(59,130,246,0.05);border:1px solid rgba(59,130,246,0.2);border-radius:10px;padding:.85rem 1rem;margin:.5rem 0;}
.rag-pill{background:var(--accent2);color:#fff;border-radius:20px;padding:.18rem .6rem;font-size:.68rem;font-weight:700;}

.crm-header{background:linear-gradient(135deg,#0D1A2E,#112240);border:1px solid var(--border);border-top:2px solid var(--accent);border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1.25rem;display:flex;justify-content:space-between;align-items:center;}
.crm-kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem;margin-bottom:1.25rem;}
.crm-kpi{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1rem;position:relative;overflow:hidden;}
.crm-kpi-bar{position:absolute;top:0;left:0;width:3px;height:100%;border-radius:12px 0 0 12px;}
.crm-kpi-val{font-family:'Syne',sans-serif;font-size:1.45rem;font-weight:800;color:#fff;}
.crm-kpi-lbl{font-size:.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-top:.2rem;}
.crm-kpi-sub{font-size:.75rem;color:var(--muted);margin-top:.1rem;}
.divider{border:none;border-top:1px solid var(--border);margin:1rem 0;}
.prog-track{background:var(--border);border-radius:4px;height:4px;margin-top:.35rem;}
.prog-fill{height:4px;border-radius:4px;}

.stButton>button{background:linear-gradient(135deg,#00D4AA 0%,#00B894 100%)!important;color:#0A0E1A!important;border:none!important;border-radius:10px!important;font-weight:700!important;font-family:'Space Grotesk',sans-serif!important;font-size:.95rem!important;padding:.75rem 1.5rem!important;width:100%!important;transition:opacity .2s!important;}
.stButton>button:hover{opacity:.88!important;}

[data-testid="stSidebar"]{background:#080C16!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *:not(button){color:#94A3B8!important;}
[data-testid="stSidebar"] h3{color:var(--accent)!important;font-family:'Syne',sans-serif!important;}
[data-testid="stSidebar"] .stTextInput input,[data-testid="stSidebar"] .stSelectbox>div>div{background:#111827!important;border-color:var(--border)!important;color:var(--text)!important;}
[data-testid="stSidebar"] .stButton>button{background:var(--surface)!important;color:var(--text)!important;border:1px solid var(--border)!important;}

.stTextInput input,.stTextArea textarea,.stSelectbox>div>div,.stNumberInput input{background:#111827!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:8px!important;font-family:'Space Grotesk',sans-serif!important;}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(0,212,170,0.15)!important;}

label,.stSelectbox label,.stTextInput label,.stTextArea label,.stNumberInput label{color:#94A3B8!important;font-size:.78rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:.06em!important;}

div[data-baseweb="tab-list"]{background:var(--surface)!important;border-bottom:1px solid var(--border)!important;border-radius:10px 10px 0 0!important;padding:.25rem .5rem 0!important;gap:.25rem!important;}
div[data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;font-size:.85rem!important;border-bottom:2px solid transparent!important;padding:.6rem .9rem!important;}
div[aria-selected="true"][data-baseweb="tab"]{color:var(--accent)!important;border-bottom:2px solid var(--accent)!important;}

.stMetric{background:var(--card)!important;border-radius:10px!important;padding:.75rem!important;}
.stMetric label{color:var(--muted)!important;font-size:.72rem!important;}
.stMetric [data-testid="stMetricValue"]{color:#fff!important;font-family:'Syne',sans-serif!important;}

[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:10px!important;}
[data-testid="stExpander"] summary{color:var(--text)!important;}

.stDownloadButton>button{background:rgba(59,130,246,0.12)!important;color:var(--accent2)!important;border:1px solid rgba(59,130,246,0.3)!important;border-radius:8px!important;font-weight:600!important;font-size:.82rem!important;}
.stDownloadButton>button:hover{background:rgba(59,130,246,0.22)!important;}

.stSuccess{background:rgba(0,212,170,0.1)!important;border-color:var(--accent)!important;color:var(--accent)!important;}
.stWarning{background:rgba(245,158,11,0.1)!important;border-color:var(--warn)!important;color:var(--warn)!important;}
.stError{background:rgba(239,68,68,0.1)!important;border-color:var(--danger)!important;color:#FCA5A5!important;}
.stInfo{background:rgba(59,130,246,0.1)!important;border-color:var(--accent2)!important;color:#93C5FD!important;}

[data-testid="stProgress"]>div>div{background:var(--accent)!important;}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
if "crm_entries" not in st.session_state:
    st.session_state["crm_entries"] = _load_crm()
for key, default in [("proposal", None), ("client_data", None), ("proposal_history", [])]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── HERO BANNER ───────────────────────────────────────────────────────────────
n_leads        = len(st.session_state["crm_entries"])
total_pipeline = sum(e["deal"].get("weighted_value", 0) for e in st.session_state["crm_entries"])

st.markdown(f"""
<div class="hackathon-banner">
  <div style="flex;">
    <div class="banner-title">AI Sales <span>Proposal Generator</span><br>+ CRM Auto-Updater</div>
    
  </div>
  <div style="display:flex;gap:.75rem;flex-shrink:0;">
    <div class="bstat"><div class="bstat-val">{n_leads}</div><div class="bstat-lbl">Leads</div></div>
    <div class="bstat"><div class="bstat-val">${total_pipeline:,}</div><div class="bstat-lbl">Pipeline</div></div>
    <div class="bstat"><div class="bstat-val">LLM</div><div class="bstat-lbl">Powered</div></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── WORKFLOW INDICATOR ────────────────────────────────────────────────────────
has_proposal = st.session_state["proposal"] is not None
s2 = "done" if has_proposal else ""
s3 = "done" if has_proposal else ""

st.markdown(f"""
<div class="workflow-row">
  <div class="wf-step active"><div class="wf-icon">👤</div><div><div class="wf-label">1. Client Info<br>Input</div></div></div>
  <div class="wf-arrow">›</div>
  <div class="wf-step {s2}"><div class="wf-icon">🤖</div><div><div class="wf-label">2. AI Proposal<br>Generation</div></div></div>
  <div class="wf-arrow">›</div>
  <div class="wf-step {s2}"><div class="wf-icon">💰</div><div><div class="wf-label">3. Pricing<br>Options</div></div></div>
  <div class="wf-arrow">›</div>
  <div class="wf-step {s3}"><div class="wf-icon">📧</div><div><div class="wf-label">4. Follow-up<br>Email Draft</div></div></div>
  <div class="wf-arrow">›</div>
  <div class="wf-step {s3}"><div class="wf-icon">📊</div><div><div class="wf-label">5. CRM<br>Auto-Update</div></div></div>
  <div class="wf-arrow">›</div>
  <div class="wf-step {s3}"><div class="wf-icon">💾</div><div><div class="wf-label">6. JSON/CSV<br>Export</div></div></div>
</div>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    default_key = os.getenv("GEMINI_API_KEY", "")
    if default_key and default_key != "your_gemini_api_key_here":
        gemini_key = default_key
        st.success("✅ API Key loaded")
    else:
        gemini_key = st.text_input("Gemini API Key", type="password", help="aistudio.google.com")

    model_choice = st.selectbox("LLM Model",
        ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"], index=0)
    os.environ["GEMINI_MODEL"] = model_choice

    st.markdown("---")
    st.markdown("### 🧠 RAG Settings")
    top_k      = st.slider("Similar proposals (k)", 1, 5, 2)
    use_filter = st.checkbox("Industry filter", value=True)

    st.markdown("---")
    st.markdown("### 🗄️ Vector DB")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🌱 Seed"):
            if not gemini_key:
                st.warning("Add API key first!")
            else:
                with st.spinner("Seeding..."):
                    try:
                        from proposal_generator import ProposalGenerator
                        gen = ProposalGenerator(api_key=gemini_key)
                        gen.seed_demo_data()
                        st.success("✅ Seeded!")
                    except Exception as e:
                        st.error(str(e))
    with col_b:
        if st.button("📊 Stats"):
            try:
                from rag_engine import RAGEngine
                st.json(RAGEngine().stats())
            except Exception as e:
                st.error(str(e))

    _n = len(st.session_state["crm_entries"])
    if _n > 0:
        st.markdown("---")
        st.markdown(f"### 📊 CRM ({_n} leads)")
        st.download_button("📦 Export JSON",
            data=json.dumps(st.session_state["crm_entries"], indent=2, ensure_ascii=False),
            file_name="crm_all.json", mime="application/json", use_container_width=True)
        st.download_button("📋 Export CSV",
            data=_entries_to_csv(st.session_state["crm_entries"]),
            file_name="crm_leads.csv", mime="text/csv", use_container_width=True)
        if st.button("🗑️ Clear CRM", use_container_width=True):
            st.session_state["crm_entries"] = []
            _save_crm([])
            st.rerun()

    if st.session_state["proposal_history"]:
        st.markdown("---")
        st.markdown("### 📚 History")
        for i, h in enumerate(reversed(st.session_state["proposal_history"][-5:])):
            if st.button(f"📄 {h['company']} · {h['roi']}% ROI", key=f"hist_{i}"):
                st.session_state["proposal"]    = h["proposal"]
                st.session_state["client_data"] = h["client"]
                st.rerun()

    st.markdown("---")
    st.markdown("""<div style='font-size:.75rem;color:#475569;line-height:1.9;'>
<strong style='color:#00D4AA;'>Prerequisites: LLM</strong><br>
🤖 Gemini 2.5 Flash<br>🔍 FAISS Vector Search<br>
🧮 sentence-transformers<br>🐍 Python + Streamlit<br>💾 JSON / CSV Export
</div>""", unsafe_allow_html=True)


# ── MAIN TABS ─────────────────────────────────────────────────────────────────
tab_gen, tab_crm = st.tabs(["🚀 Generate Proposal", "📊 CRM Dashboard"])


# ══════════════════════════════════════════════════════
# TAB 1 — GENERATE PROPOSAL
# ══════════════════════════════════════════════════════
with tab_gen:

    st.markdown('<div class="sec-label">Step 1 — Salesperson enters client details</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1.1, 1])
    with col_l:
        company_name = st.text_input("Client / Company Name *", placeholder="e.g. HealthAI Solutions Ltd.")
        col_ind, col_team = st.columns(2)
        with col_ind:
            industry = st.selectbox("Sector / Industry *", [
                "Healthcare","Fintech","E-commerce","SaaS","EdTech",
                "Logistics","Manufacturing","Real Estate","LegalTech","Other"
            ])
        with col_team:
            team_size = st.number_input("Team Size", min_value=1, value=50, step=10)
        current_rev = st.number_input("Current Annual Revenue ($)", min_value=0,
                                       value=2_000_000, step=100_000, format="%d")
        problem = st.text_area("Client Requirements / Problem Statement *",
            placeholder="e.g. Patient onboarding takes 3x industry average. Manual data entry wastes 40% of staff time...",
            height=110)

    with col_r:
        goals = st.text_area("Business Goals *",
            placeholder="e.g. Automate 70% of workflows, reduce CAC by 40%, scale to 10x users...",
            height=90)
        col_bmin, col_bmax = st.columns(2)
        with col_bmin:
            budget_min = st.number_input("Budget Min ($)", min_value=10_000,
                                          value=100_000, step=10_000, format="%d")
        with col_bmax:
            budget_max = st.number_input("Budget Max ($)", min_value=10_000,
                                          value=500_000, step=10_000, format="%d")
        timeline = st.slider("Engagement Duration (months)", 3, 24, 12)
        st.markdown(f"""
        <div style='background:var(--card);border:1px solid var(--border);border-radius:10px;
        padding:.85rem 1rem;margin-top:.25rem;'>
          <div style='font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.35rem;'>Budget Range</div>
          <div style='font-size:1.1rem;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>${budget_min:,} — ${budget_max:,}</div>
          <div style='font-size:.75rem;color:var(--muted);margin-top:.2rem;'>Midpoint: ${(budget_min+budget_max)//2:,} · {timeline} months</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Step 2 — One click: AI generates proposal + email + updates CRM</div>', unsafe_allow_html=True)
    gen_btn = st.button("⚡  Generate AI Proposal  +  Draft Follow-up Email  +  Auto-Update CRM", use_container_width=True)

    if gen_btn:
        if not gemini_key or gemini_key == "your_gemini_api_key_here":
            st.error("⚠️ Add your Gemini API key in the sidebar.")
            st.stop()
        if not company_name:
            st.error("⚠️ Client / Company Name is required.")
            st.stop()
        if not problem or not goals:
            st.error("⚠️ Problem Statement and Goals are required.")
            st.stop()
        if budget_max < budget_min:
            st.error("⚠️ Budget Max must be ≥ Budget Min.")
            st.stop()

        client_data = {
            "company_name":      company_name,
            "industry":          industry,
            "problem_statement": problem,
            "goals":             goals,
            "budget_min":        budget_min,
            "budget_max":        budget_max,
            "timeline_months":   timeline,
            "team_size":         team_size,
            "current_revenue":   current_rev,
        }
        filters      = {"industry": industry} if use_filter else None
        progress_bar = st.progress(0)
        status       = st.status("🤖 LLM pipeline running...", expanded=True)

        try:
            with status:
                st.write("🔧 Initializing Gemini + RAG engine...")
                progress_bar.progress(10)
                from proposal_generator import ProposalGenerator
                gen = ProposalGenerator(api_key=gemini_key)
                st.write(f"🔍 FAISS searching similar {industry} proposals...")
                progress_bar.progress(28)
                st.write("🤖 Gemini generating formatted proposal with pricing options...")
                progress_bar.progress(50)
                proposal = gen.generate(client_data, k=top_k, filters=filters)
                st.write("📐 Validating JSON + ROI math...")
                progress_bar.progress(72)
                st.write("📧 Drafting personalised follow-up email...")
                progress_bar.progress(88)
                st.write("💾 Auto-updating CRM — JSON + CSV ready...")
                progress_bar.progress(100)
            status.update(label="✅ Done! Proposal generated · Email drafted · CRM updated", state="complete")

            st.session_state["proposal"]    = proposal
            st.session_state["client_data"] = client_data

            crm_entry = _build_crm_entry(proposal, client_data)
            existing  = [e for e in st.session_state["crm_entries"]
                         if e["lead_info"]["name"].lower() != company_name.strip().lower()]
            existing.insert(0, crm_entry)
            st.session_state["crm_entries"] = existing
            _save_crm(existing)

            st.session_state["proposal_history"].append({
                "company": company_name, "industry": industry,
                "roi": proposal.get("roi_percentage", "N/A"),
                "inv": proposal.get("total_investment", 0),
                "time": datetime.now().strftime("%H:%M"),
                "proposal": proposal, "client": client_data,
            })
            st.balloons()

        except Exception as e:
            err = str(e).lower()
            if "quota" in err or "429" in err or "rate" in err:
                status.update(label="❌ API quota exceeded", state="error")
                st.error("⚠️ Rate limit. Wait 30s or switch model.")
            elif "api key" in err or "invalid" in err or "permission" in err:
                status.update(label="❌ Invalid API key", state="error")
                st.error("⚠️ Invalid API key. Check aistudio.google.com")
            elif "json" in err or "parse" in err:
                status.update(label="❌ Parse failed", state="error")
                st.error("⚠️ JSON parsing failed. Try again.")
            else:
                status.update(label="❌ Error", state="error")
                st.error(f"Error: {e}")
            st.info("💡 Seed demo data from the sidebar first.")

    # ── RESULTS ───────────────────────────────────────────────────────────────
    if st.session_state["proposal"] and st.session_state["client_data"]:
        p  = st.session_state["proposal"]
        cd = st.session_state["client_data"]

        st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-label">Step 3 — Review AI-generated outputs</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:rgba(0,212,170,0.07);border:1px solid rgba(0,212,170,0.2);
        border-radius:10px;padding:.65rem 1.1rem;margin-bottom:1rem;
        display:flex;gap:1.5rem;align-items:center;flex-wrap:wrap;font-size:.78rem;'>
          <span style='color:var(--accent);font-weight:700;'>✅ GENERATED</span>
          <span style='color:var(--muted);'>🏢 {cd['company_name']}</span>
          <span style='color:var(--muted);'>🏭 {cd['industry']}</span>
          <span style='color:var(--muted);'>🤖 {model_choice}</span>
          <span style='color:var(--muted);'>🔍 {p.get("_rag_count",0)} RAG sources</span>
          <span style='color:var(--accent);font-weight:700;'>📊 CRM Auto-updated ✓</span>
          <span style='color:var(--accent);font-weight:700;'>📧 Email drafted ✓</span>
        </div>
        """, unsafe_allow_html=True)

        inv       = p.get("total_investment", 0)
        roi       = p.get("roi_percentage", 0)
        total_rev = sum(p.get("monthly_revenue_projection", []))
        pb        = p.get("payback_period_months", "N/A")

        st.markdown(f"""
        <div class="kpi-grid">
          <div class="kpi-box kpi-green">
            <div class="kpi-val">{roi}%</div><div class="kpi-lbl">Projected ROI</div>
            <div class="kpi-sub">Revenue return</div>
          </div>
          <div class="kpi-box kpi-blue">
            <div class="kpi-val">${inv:,}</div><div class="kpi-lbl">Proposal Price</div>
            <div class="kpi-sub">Total investment</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-val">${total_rev:,}</div><div class="kpi-lbl">12-Month Revenue</div>
            <div class="kpi-sub">Projected</div>
          </div>
          <div class="kpi-box kpi-amber">
            <div class="kpi-val">{pb} mo</div><div class="kpi-lbl">Payback Period</div>
            <div class="kpi-sub">Break-even</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        r_tab1, r_tab2, r_tab3, r_tab4 = st.tabs([
            "📄 Proposal + Pricing",
            "📧 Follow-up Email",
            "🔍 RAG Context",
            "💾 Export JSON/CSV",
        ])

        with r_tab1:
            st.markdown('<div class="sec-label">Executive Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="output-card">{p.get("executive_summary","")}</div>', unsafe_allow_html=True)

            pa = p.get("problem_analysis", {})
            if pa:
                st.markdown('<div class="sec-label">Problem Analysis</div>', unsafe_allow_html=True)
                cc1, cc2 = st.columns([3,1])
                with cc1:
                    for ch in pa.get("primary_challenges", []):
                        st.markdown(f'<div class="challenge-pill">⚠ {ch}</div>', unsafe_allow_html=True)
                with cc2:
                    st.metric("Revenue Impact", pa.get("revenue_impact", "N/A"))

            phases = p.get("proposed_solution", {}).get("phases", [])
            if phases:
                st.markdown('<div class="sec-label">Implementation Phases</div>', unsafe_allow_html=True)
                for i, phase in enumerate(phases):
                    with st.expander(f"{phase.get('phase','Phase')} — {phase.get('name','')}  ·  {phase.get('duration','')}", expanded=(i==0)):
                        for d in phase.get("key_deliverables", []):
                            st.markdown(f"→ {d}")

            rev_data = p.get("monthly_revenue_projection", [])
            if rev_data:
                st.markdown('<div class="sec-label">Monthly Revenue Projection</div>', unsafe_allow_html=True)
                import pandas as pd
                df = pd.DataFrame({"Month": [f"M{i+1}" for i in range(len(rev_data))], "Revenue ($)": rev_data}).set_index("Month")
                st.line_chart(df, height=220)

            ba = p.get("budget_allocation", {})
            if ba:
                st.markdown('<div class="sec-label">Pricing / Budget Allocation</div>', unsafe_allow_html=True)
                b_cols = st.columns(len(ba))
                for (cat, pct), col in zip(ba.items(), b_cols):
                    col.metric(cat.upper(), f"{pct}%", f"${int(inv * pct / 100):,}")

            why = p.get("why_us", [])
            if why:
                st.markdown('<div class="sec-label">Why Choose Us</div>', unsafe_allow_html=True)
                for point in why:
                    st.markdown(f"✦ {point}")

            nxt = p.get("next_steps","")
            if nxt:
                st.markdown('<div class="sec-label">Next Steps</div>', unsafe_allow_html=True)
                st.info(nxt)

        with r_tab2:
            email_raw = p.get("_followup_email", "")
            if email_raw:
                lines   = email_raw.strip().split("\n")
                subject = next((l.split(":",1)[1].strip() for l in lines if l.lower().startswith("subject:")), "")
                body    = "\n".join(l for l in lines if not l.lower().startswith("subject:")).strip()
                if subject:
                    st.markdown(f"""
                    <div style='background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.25);
                    border-radius:8px;padding:.65rem 1rem;margin-bottom:.85rem;'>
                      <span style='color:var(--muted);font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;'>Subject Line</span><br>
                      <span style='color:#93C5FD;font-weight:700;font-size:.95rem;'>{subject}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f'<div class="email-output">{body}</div>', unsafe_allow_html=True)
                ec1, ec2 = st.columns(2)
                with ec1:
                    st.text_area("✏️ Edit before sending", value=body, height=180, key="email_edit")
                with ec2:
                    st.download_button("📋 Download Email (.txt)", data=email_raw,
                        file_name=f"email_{cd['company_name'].replace(' ','_')}.txt",
                        mime="text/plain", use_container_width=True)
            else:
                st.info("Email not generated. Try regenerating.")

        with r_tab3:
            rag_sources = p.get("_rag_sources", [])
            if rag_sources:
                st.markdown(f"""
                <div style='background:rgba(59,130,246,0.07);border:1px solid rgba(59,130,246,0.2);
                border-radius:10px;padding:.75rem 1rem;margin-bottom:.75rem;font-size:.85rem;color:#93C5FD;'>
                🔍 <strong>{len(rag_sources)} similar proposal(s)</strong> retrieved from FAISS — injected into LLM prompt for industry-specific, grounded output.
                </div>
                """, unsafe_allow_html=True)
                for src in rag_sources:
                    sc = int(src["score"] * 100)
                    bc = "#00D4AA" if sc >= 70 else "#F59E0B" if sc >= 45 else "#64748B"
                    st.markdown(f"""
                    <div class="rag-card">
                      <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <div><strong style='color:#fff;'>{src['company']}</strong>
                          <span style='color:var(--muted);font-size:.8rem;margin-left:.5rem;'>— {src['industry']}</span></div>
                        <span class="rag-pill">Similarity {sc}%</span>
                      </div>
                      <div style='display:flex;gap:1.5rem;margin:.4rem 0;'>
                        <span style='font-size:.8rem;color:#93C5FD;font-weight:600;'>ROI: {src['roi']}%</span>
                        <span style='font-size:.8rem;color:#93C5FD;font-weight:600;'>Budget: ${src['budget']:,}</span>
                      </div>
                      <div style='background:var(--border);border-radius:4px;height:4px;'>
                        <div style='background:{bc};border-radius:4px;height:4px;width:{sc}%;'></div></div>
                      <div style='font-size:.78rem;color:var(--muted);margin-top:.4rem;font-style:italic;'>"{src['summary']}"</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No RAG sources retrieved. Seed demo data from the sidebar first.")

        with r_tab4:
            st.markdown("""
            <div style='background:rgba(0,212,170,0.07);border:1px solid rgba(0,212,170,0.2);
            border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.85rem;color:#6EE7B7;'>
            ✅ CRM has been <strong>auto-updated</strong>. Export below for your CRM system.
            </div>
            """, unsafe_allow_html=True)
            dl1, dl2, dl3 = st.columns(3)
            with dl1:
                fp = json.dumps({"client": cd, "proposal": {k:v for k,v in p.items() if not k.startswith("_")}}, indent=2)
                st.download_button("📦 Full Proposal JSON", data=fp,
                    file_name=f"proposal_{cd['company_name'].replace(' ','_')}.json",
                    mime="application/json", use_container_width=True)
            with dl2:
                st.download_button("🧹 Clean JSON",
                    data=json.dumps({k:v for k,v in p.items() if not k.startswith("_")}, indent=2),
                    file_name=f"clean_{cd['company_name'].replace(' ','_')}.json",
                    mime="application/json", use_container_width=True)
            with dl3:
                st.download_button("📧 Email (.txt)",
                    data=p.get("_followup_email",""),
                    file_name=f"email_{cd['company_name'].replace(' ','_')}.txt",
                    mime="text/plain", use_container_width=True)
            st.markdown("#### Proposal JSON Preview")
            st.json({k:v for k,v in p.items() if not k.startswith("_")})


# ══════════════════════════════════════════════════════
# TAB 2 — CRM DASHBOARD (always visible)
# ══════════════════════════════════════════════════════
with tab_crm:
    entries = st.session_state["crm_entries"]
    n_crm   = len(entries)

    if not entries:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;'>
          <div style='font-size:3rem;margin-bottom:1rem;'>📊</div>
          <div style='font-family:Syne,sans-serif;font-size:1.2rem;font-weight:800;color:#fff;'>CRM is empty</div>
          <div style='font-size:.9rem;color:var(--muted);max-width:420px;margin:.75rem auto 0;line-height:1.7;'>
            Generate a proposal in the first tab.<br>
            It will <strong style='color:var(--accent);'>automatically appear here — no manual entry needed.</strong><br><br>
            <span style='font-size:.8rem;'>Data persists via <code style='background:var(--surface);padding:.1rem .4rem;border-radius:4px;'>crm_data.json</code></span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        total_wt = sum(e["deal"].get("weighted_value", 0) for e in entries)
        n_won    = len([e for e in entries if e["deal"]["stage"] == "Closed Won"])
        win_rate = round(n_won / n_crm * 100) if n_crm else 0
        avg_roi  = round(sum(e["proposal_metadata"].get("roi", 0) for e in entries) / n_crm)

        st.markdown(f"""
        <div class="crm-header">
          <div>
            <div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:#fff;'>📊 CRM — Auto-Updated</div>
            <div style='font-size:.75rem;color:var(--muted);margin-top:.2rem;'>
              {n_crm} lead{"s" if n_crm!=1 else ""} &nbsp;·&nbsp;
              {datetime.now():%d %b %Y, %H:%M} &nbsp;·&nbsp;
              JSON + CSV export ready
            </div>
          </div>
          <div style='display:flex;gap:1.25rem;'>
            <div style='text-align:center;'>
              <div style='font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:var(--accent);'>{n_crm}</div>
              <div style='font-size:.65rem;color:var(--muted);text-transform:uppercase;'>Leads</div>
            </div>
            <div style='text-align:center;'>
              <div style='font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:var(--accent2);'>${total_wt:,}</div>
              <div style='font-size:.65rem;color:var(--muted);text-transform:uppercase;'>Pipeline</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="crm-kpi-grid">
          <div class="crm-kpi"><div class="crm-kpi-bar" style="background:#3B82F6;"></div>
            <div class="crm-kpi-val">{n_crm}</div><div class="crm-kpi-lbl">Total Leads</div>
            <div class="crm-kpi-sub">Proposals sent</div></div>
          <div class="crm-kpi"><div class="crm-kpi-bar" style="background:#00D4AA;"></div>
            <div class="crm-kpi-val">{n_won}</div><div class="crm-kpi-lbl">Closed Won</div>
            <div class="crm-kpi-sub">Converted</div></div>
          <div class="crm-kpi"><div class="crm-kpi-bar" style="background:#F59E0B;"></div>
            <div class="crm-kpi-val">{win_rate}%</div><div class="crm-kpi-lbl">Win Rate</div>
            <div class="crm-kpi-sub">Closed ÷ Total</div></div>
          <div class="crm-kpi"><div class="crm-kpi-bar" style="background:#8B5CF6;"></div>
            <div class="crm-kpi-val">{avg_roi}%</div><div class="crm-kpi-lbl">Avg ROI</div>
            <div class="crm-kpi-sub">Across proposals</div></div>
        </div>
        """, unsafe_allow_html=True)

        import pandas as pd
        ind_map = {}
        for e in entries:
            ind = e["lead_info"]["industry"]
            ind_map[ind] = ind_map.get(ind, 0) + 1
        if len(ind_map) >= 2:
            st.markdown('<div style="font-size:.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin:.5rem 0;">Leads by Sector</div>', unsafe_allow_html=True)
            df_i = pd.DataFrame({"Sector": list(ind_map.keys()), "Leads": list(ind_map.values())}).set_index("Sector")
            st.bar_chart(df_i, height=150)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filt_s = st.selectbox("Filter Stage",
                ["All","Proposal Sent","Qualified","Negotiation","Closed Won","Closed Lost"],
                key="crm_filt_s")
        with fc2:
            inds   = ["All"] + sorted({e["lead_info"]["industry"] for e in entries})
            filt_i = st.selectbox("Filter Sector", inds, key="crm_filt_i")
        with fc3:
            sort = st.selectbox("Sort By",
                ["Latest First","Highest ROI","Highest Value"], key="crm_sort")

        filtered = entries[:]
        if filt_s != "All": filtered = [e for e in filtered if e["deal"]["stage"] == filt_s]
        if filt_i != "All": filtered = [e for e in filtered if e["lead_info"]["industry"] == filt_i]
        if sort == "Highest ROI":    filtered.sort(key=lambda x: x["proposal_metadata"].get("roi",0), reverse=True)
        elif sort == "Highest Value": filtered.sort(key=lambda x: x["lead_info"].get("budget_num",0), reverse=True)

        st.markdown(f"""
        <div style='font-size:.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin:.5rem 0;'>
        All Leads <span style='background:rgba(59,130,246,0.15);color:#93C5FD;border-radius:20px;padding:.1rem .55rem;font-size:.65rem;'>{len(filtered)}</span>
        </div>
        """, unsafe_allow_html=True)

        STAGE_STYLE = {
            "Proposal Sent": ("#1A2B1A","#6EE7B7","#00D4AA"),
            "Qualified":     ("#1A1A2B","#93C5FD","#3B82F6"),
            "Negotiation":   ("#2B1A1A","#FCA5A5","#EF4444"),
            "Closed Won":    ("#0D2B1A","#6EE7B7","#00D4AA"),
            "Closed Lost":   ("#1A1A1A","#64748B","#374151"),
        }
        STAGE_PROB = {"Proposal Sent":55,"Qualified":30,"Negotiation":75,"Closed Won":100,"Closed Lost":0}

        for idx, entry in enumerate(filtered):
            li    = entry["lead_info"]
            deal  = entry["deal"]
            meta  = entry.get("proposal_metadata", {})
            fu_e  = entry.get("follow_up_email", {})
            stage = deal.get("stage", "Proposal Sent")
            prob  = deal.get("probability", 55)
            wval  = deal.get("weighted_value", 0)
            sbg, sfg, sborder = STAGE_STYLE.get(stage, ("#111827","#93C5FD","#3B82F6"))
            try:
                orig_idx = st.session_state["crm_entries"].index(entry)
            except ValueError:
                orig_idx = idx

            with st.expander(
                f"🏢  {li['name']}  ·  {li['industry']}  ·  {li.get('estimated_value','N/A')}  ·  {stage}",
                expanded=(idx == 0)
            ):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("💰 Budget",      li.get("estimated_value","N/A"))
                m2.metric("📊 Probability", f"{prob}%")
                m3.metric("🎯 Weighted",    f"${wval:,}")
                m4.metric("📈 ROI",         f"{meta.get('roi',0)}%")

                st.markdown(f"""
                <div style='margin:.6rem 0 .25rem;'>
                  <span style='background:{sbg};color:{sfg};border:1px solid {sborder};
                  font-size:.7rem;font-weight:700;padding:.2rem .7rem;border-radius:20px;'>{stage}</span>
                  <span style='font-size:.75rem;color:var(--muted);margin-left:.7rem;'>
                  {prob}% probability · Payback: {meta.get('payback','N/A')} months · Added: {li.get('added_at','')}</span>
                </div>
                <div class="prog-track"><div class="prog-fill" style="width:{prob}%;background:{sborder};"></div></div>
                """, unsafe_allow_html=True)

                summary = meta.get("summary","")
                if summary:
                    st.markdown(f"""
                    <div style='background:var(--surface);border:1px solid var(--border);
                    border-left:3px solid var(--accent2);border-radius:8px;
                    padding:.7rem 1rem;margin:.7rem 0;font-size:.84rem;color:#CBD5E1;line-height:1.6;'>📝 {summary}</div>
                    """, unsafe_allow_html=True)

                if fu_e:
                    subj = fu_e.get("subject","") if isinstance(fu_e, dict) else ""
                    body = fu_e.get("body","") if isinstance(fu_e, dict) else str(fu_e)
                    with st.expander("📧 Follow-up Email Draft"):
                        if subj:
                            st.markdown(f"**Subject:** {subj}")
                        body_clean = "\n".join(l for l in body.split("\n") if not l.lower().startswith("subject:")).strip()
                        st.markdown(f'<div class="email-output" style="max-height:260px;overflow-y:auto;">{body_clean}</div>', unsafe_allow_html=True)

                st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                sc1, sc2, sc3 = st.columns([3,1,1])
                with sc1:
                    stage_opts = ["Proposal Sent","Qualified","Negotiation","Closed Won","Closed Lost"]
                    cur_idx    = stage_opts.index(stage) if stage in stage_opts else 0
                    new_stage  = st.selectbox("Update Stage", stage_opts, index=cur_idx, key=f"crm_stage_{orig_idx}")
                    if st.button("✅ Update", key=f"crm_upd_{orig_idx}"):
                        new_prob = STAGE_PROB.get(new_stage, 55)
                        st.session_state["crm_entries"][orig_idx]["deal"]["stage"]          = new_stage
                        st.session_state["crm_entries"][orig_idx]["lead_info"]["status"]    = new_stage
                        st.session_state["crm_entries"][orig_idx]["deal"]["probability"]    = new_prob
                        st.session_state["crm_entries"][orig_idx]["deal"]["weighted_value"] = int(li.get("budget_num",0) * new_prob / 100)
                        _save_crm(st.session_state["crm_entries"])
                        st.success(f"✅ Stage → {new_stage}")
                        st.rerun()
                with sc2:
                    st.download_button("📦 JSON",
                        data=json.dumps(entry, indent=2, ensure_ascii=False),
                        file_name=f"crm_{li['name'].replace(' ','_')}.json",
                        mime="application/json", key=f"crm_dlj_{orig_idx}", use_container_width=True)
                with sc3:
                    buf = io.StringIO()
                    w   = csv.DictWriter(buf, fieldnames=["name","industry","budget","status","stage","probability","roi","payback","added_at"])
                    w.writeheader()
                    w.writerow({
                        "name": li["name"], "industry": li["industry"],
                        "budget": li.get("estimated_value",""), "status": li.get("status",""),
                        "stage": deal["stage"], "probability": deal["probability"],
                        "roi": meta.get("roi",""), "payback": meta.get("payback",""),
                        "added_at": li.get("added_at",""),
                    })
                    st.download_button("📋 CSV",
                        data=buf.getvalue().encode(),
                        file_name=f"crm_{li['name'].replace(' ','_')}.csv",
                        mime="text/csv", key=f"crm_dlc_{orig_idx}", use_container_width=True)
