"""
app.py  —  Streamlit UI for AI Sales Intelligence Platform
Run: streamlit run app.py
"""

import os
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "AI Sales Intelligence",
    page_icon  = "⚡",
    layout     = "wide",
    initial_sidebar_state = "expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #1e40af 100%);
    padding: 2.5rem 2rem; border-radius: 20px; margin-bottom: 2rem;
    text-align: center; position: relative; overflow: hidden;
  }
  .hero h1  { color: #fff; font-size: 2.4rem; font-weight: 800; margin: 0 0 0.5rem; letter-spacing: -0.5px; }
  .hero p   { color: #93c5fd; font-size: 1rem; margin: 0; }
  .hero .badges { margin-top: 1rem; }
  .badge {
    display: inline-block; background: rgba(255,255,255,0.15); color: #e0f2fe;
    border: 1px solid rgba(255,255,255,0.2); border-radius: 20px;
    padding: 0.25rem 0.9rem; font-size: 0.72rem; font-weight: 600;
    margin: 0.2rem; letter-spacing: 0.04em;
  }

  .kpi-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 1.4rem 1rem; text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); transition: box-shadow 0.2s;
  }
  .kpi-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
  .kpi-val   { font-size: 2rem; font-weight: 800; color: #1e3a5f; line-height: 1; }
  .kpi-label { font-size: 0.72rem; color: #64748b; text-transform: uppercase;
               letter-spacing: 0.06em; margin-top: 0.4rem; }
  .kpi-green .kpi-val { color: #059669; }
  .kpi-blue  .kpi-val { color: #2563eb; }

  .section-title {
    font-size: 1.05rem; font-weight: 700; color: #1e3a5f;
    border-left: 4px solid #3b82f6; padding-left: 0.75rem;
    margin: 1.8rem 0 1rem;
  }

  .summary-box {
    background: #f8fafc; border: 1px solid #dbeafe;
    border-radius: 12px; padding: 1.25rem 1.5rem;
    font-size: 0.95rem; line-height: 1.7; color: #334155;
  }

  .challenge-item {
    background: #fff1f2; border-left: 3px solid #f43f5e;
    border-radius: 6px; padding: 0.6rem 0.9rem; margin: 0.4rem 0;
    font-size: 0.9rem; color: #881337;
  }

  .phase-card {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 0.9rem 1.1rem; margin: 0.4rem 0;
    border-left: 4px solid #3b82f6;
  }

  .rag-context {
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 10px; padding: 0.75rem 1rem;
    font-size: 0.82rem; color: #1e40af; margin-bottom: 1rem;
  }

  .math-check {
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-radius: 8px; padding: 0.5rem 1rem;
    font-size: 0.8rem; color: #166534; font-family: monospace;
  }

  .stButton > button {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%) !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    padding: 0.8rem 1.5rem !important; font-weight: 700 !important;
    font-size: 1rem !important; width: 100% !important;
    letter-spacing: 0.02em !important; transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.88 !important; }

  [data-testid="stSidebar"] { background: #191A1C; }
</style>
""", unsafe_allow_html=True)

# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>⚡ AI Sales Intelligence Platform</h1>
  <p>Generate personalized, data-driven proposals in seconds using RAG + Gemini</p>
  <div class="badges">
    <span class="badge">🧠 FAISS Vector Search</span>
    <span class="badge">🤖 Google Gemini 2.5 Flash</span>
    <span class="badge">📐 Math-Validated JSON</span>
    <span class="badge">♻️ Continuous Learning</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # API key from .env or manual input
    default_key = os.getenv("GEMINI_API_KEY", "")
    if default_key and default_key != "your_gemini_api_key_here":
        st.success("✅ API Key loaded from .env")
        gemini_key = default_key
    else:
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Get free key at aistudio.google.com"
        )

    model_choice = st.selectbox(
        "Gemini Model",
        ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        index=0,
        help="gemini-2.5-flash is fastest and free-tier friendly"
    )
    os.environ["GEMINI_MODEL"] = model_choice

    st.markdown("---")
    st.markdown("### 🧠 RAG Settings")
    top_k      = st.slider("Proposals to retrieve (k)", 1, 5, 2)
    use_filter = st.checkbox("Industry-based filter", value=True,
                              help="Only retrieve proposals from same industry")

    st.markdown("---")
    st.markdown("### 🗄️ Vector Database")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🌱 Seed Data"):
            if not gemini_key or gemini_key == "your_gemini_api_key_here":
                st.warning("Add API key first!")
            else:
                with st.spinner("Seeding..."):
                    try:
                        from proposal_generator import ProposalGenerator
                        gen = ProposalGenerator(api_key=gemini_key)
                        gen.seed_demo_data()
                        st.success("✅ 5 proposals seeded!")
                    except Exception as e:
                        st.error(str(e))
    with col_b:
        if st.button("📊 DB Stats"):
            try:
                from rag_engine import RAGEngine
                stats = RAGEngine().stats()
                st.json(stats)
            except Exception as e:
                st.error(str(e))

    st.markdown("---")
    st.markdown("""
**Stack**
- 🤖 Google Gemini 2.5 Flash
- 🔍 FAISS (Facebook AI)
- 🧮 sentence-transformers
- 🐍 Python 3.10+
- 🖥️ Streamlit
""")


# ── Client Form ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Client Information</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    company_name = st.text_input("Company Name *", placeholder="e.g. HealthAI Solutions")
    industry     = st.selectbox("Industry *", [
        "Healthcare", "Fintech", "E-commerce", "SaaS", "EdTech",
        "Logistics", "Manufacturing", "Real Estate", "LegalTech", "Other"
    ])
    team_size   = st.number_input("Team Size", min_value=1, value=50, step=10)
    current_rev = st.number_input("Current Annual Revenue ($)", min_value=0,
                                   value=2_000_000, step=100_000,
                                   format="%d")

with c2:
    budget_min = st.number_input("Budget Min ($)", min_value=10_000,
                                  value=100_000, step=10_000, format="%d")
    budget_max = st.number_input("Budget Max ($)", min_value=10_000,
                                  value=500_000, step=10_000, format="%d")
    timeline   = st.slider("Engagement Duration (months)", 3, 24, 12)

problem = st.text_area(
    "Problem Statement *",
    placeholder="e.g. Patient onboarding takes 3x industry average. Manual workflows cost 4 hours/staff/day...",
    height=90
)
goals = st.text_area(
    "Business Goals *",
    placeholder="e.g. Automate 70% of workflows, reduce CAC by 40%, expand to 3 new markets...",
    height=70
)


# ── Generate Button ───────────────────────────────────────────────────────────
st.markdown("---")
gen_btn = st.button("🚀 Generate AI-Powered Proposal", use_container_width=True)

if gen_btn:
    # Validation
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        st.error("⚠️ Please add your Gemini API key in the sidebar or .env file.")
        st.info("Get a free key at: https://aistudio.google.com")
        st.stop()

    if not company_name:
        st.error("⚠️ Company Name is required.")
        st.stop()

    if not problem or not goals:
        st.error("⚠️ Problem Statement and Goals are required.")
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

    filters = {"industry": industry} if use_filter else None

    progress_bar = st.progress(0)
    status       = st.status("Initializing pipeline...", expanded=True)

    try:
        with status:
            st.write("🔧 Loading Gemini client and RAG engine...")
            progress_bar.progress(15)
            from proposal_generator import ProposalGenerator
            gen = ProposalGenerator(api_key=gemini_key)

            st.write(f"🔍 Searching FAISS for similar {industry} proposals...")
            progress_bar.progress(35)

            st.write("🤖 Generating with Gemini 2.5 Flash...")
            progress_bar.progress(55)
            proposal = gen.generate(client_data, k=top_k, filters=filters)

            st.write("✅ Validating JSON and math...")
            progress_bar.progress(85)

            st.write("💾 Storing new proposal in FAISS...")
            progress_bar.progress(100)

        status.update(label="✅ Proposal generated!", state="complete")
        st.session_state["proposal"]    = proposal
        st.session_state["client_data"] = client_data
        st.balloons()

    except Exception as e:
        status.update(label=f"❌ Error: {e}", state="error")
        st.error(f"Generation failed: {e}")
        st.info("💡 Tips: Make sure your API key is valid. Try seeding demo data first from the sidebar.")


# ── Results ───────────────────────────────────────────────────────────────────
if "proposal" in st.session_state:
    p  = st.session_state["proposal"]
    cd = st.session_state["client_data"]

    st.markdown("---")
    st.markdown(f"## 📄 Proposal — **{cd['company_name']}**")
    st.caption(f"Generated: {datetime.now():%Y-%m-%d %H:%M}  |  Industry: {cd['industry']}  |  Model: {model_choice}")

    # RAG + math badges
    math_check = p.get("_roi_math_check", "")
    st.markdown(f"""
    <div class="rag-context">
      🔍 <strong>RAG Context Active</strong> — Retrieved similar proposals used as generation context &nbsp;|&nbsp;
      🤖 <strong>{model_choice}</strong> &nbsp;|&nbsp;
      ✅ <strong>JSON Validated</strong>
    </div>
    {"<div class='math-check'>📐 ROI Math: " + math_check + "</div>" if math_check else ""}
    """, unsafe_allow_html=True)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    st.markdown("")
    k1, k2, k3, k4 = st.columns(4)
    inv       = p.get("total_investment", 0)
    roi       = p.get("roi_percentage", 0)
    total_rev = sum(p.get("monthly_revenue_projection", []))
    pb        = p.get("payback_period_months", "N/A")

    k1.markdown(f'<div class="kpi-card kpi-green"><div class="kpi-val">{roi}%</div><div class="kpi-label">Projected ROI</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card kpi-blue"><div class="kpi-val">${inv:,}</div><div class="kpi-label">Total Investment</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><div class="kpi-val">${total_rev:,}</div><div class="kpi-label">12-Month Revenue</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-val">{pb} mo</div><div class="kpi-label">Payback Period</div></div>', unsafe_allow_html=True)

    # ── Executive Summary ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">💼 Executive Summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-box">{p.get("executive_summary", "")}</div>', unsafe_allow_html=True)

    # ── Problem Analysis ───────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔴 Problem Analysis</div>', unsafe_allow_html=True)
    pa = p.get("problem_analysis", {})
    if pa:
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            for c in pa.get("primary_challenges", []):
                st.markdown(f'<div class="challenge-item">⚠️ {c}</div>', unsafe_allow_html=True)
        with col_p2:
            st.metric("Revenue Impact", pa.get("revenue_impact", "N/A"))

    # ── Solution Phases ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🗺️ Implementation Phases</div>', unsafe_allow_html=True)
    phases = p.get("proposed_solution", {}).get("phases", [])
    phase_colors = ["#3b82f6", "#10b981", "#f59e0b"]
    for i, phase in enumerate(phases):
        color = phase_colors[i % len(phase_colors)]
        with st.expander(
            f"{phase.get('phase')} — {phase.get('name', '')}  ·  {phase.get('duration', '')}",
            expanded = (i == 0)
        ):
            for d in phase.get("key_deliverables", []):
                st.markdown(f"✅ &nbsp; {d}")

    # ── Revenue Chart ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Monthly Revenue Projection</div>', unsafe_allow_html=True)
    rev_data = p.get("monthly_revenue_projection", [])
    if rev_data:
        import pandas as pd
        df = pd.DataFrame({
            "Month":       [f"M{i+1}" for i in range(len(rev_data))],
            "Revenue ($)": rev_data
        }).set_index("Month")
        st.line_chart(df, height=250)
        # Monthly table
        with st.expander("📋 Monthly Breakdown"):
            col_pairs = st.columns(6)
            for i, (r, col) in enumerate(zip(rev_data, col_pairs * 2)):
                col.metric(f"Month {i+1}", f"${r:,}")

    # ── Budget Allocation ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">💰 Budget Allocation</div>', unsafe_allow_html=True)
    ba = p.get("budget_allocation", {})
    if ba:
        b_cols = st.columns(len(ba))
        for (cat, pct), col in zip(ba.items(), b_cols):
            amount = int(inv * pct / 100)
            col.metric(cat.upper(), f"{pct}%", f"${amount:,}")

    # ── Why Us ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">⭐ Why Choose Us</div>', unsafe_allow_html=True)
    for point in p.get("why_us", []):
        st.markdown(f"✦ &nbsp; {point}")

    # ── Next Steps ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🚀 Next Steps</div>', unsafe_allow_html=True)
    st.info(p.get("next_steps", ""))

    # ── Downloads ──────────────────────────────────────────────────────────────
    st.markdown("---")
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            label     = "⬇️ Download Proposal JSON",
            data      = json.dumps({"client": cd, "proposal": p}, indent=2),
            file_name = f"proposal_{cd['company_name'].replace(' ', '_')}.json",
            mime      = "application/json",
        )
    with dl2:
        # Raw proposal only
        clean = {k: v for k, v in p.items() if not k.startswith("_")}
        st.download_button(
            label     = "⬇️ Download Clean JSON",
            data      = json.dumps(clean, indent=2),
            file_name = f"clean_proposal_{cd['company_name'].replace(' ', '_')}.json",
            mime      = "application/json",
        )
