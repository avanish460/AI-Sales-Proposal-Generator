"""
app.py  —  AI Sales Intelligence Platform  (main entry point)
Run:  streamlit run app.py

Files:
  app.py            ← you are here  (UI + routing)
  styles.py         ← all CSS
  utils.py          ← CRM helpers
  proposal_generator.py  ← RAG + Gemini pipeline
  rag_engine.py     ← FAISS vector store
  llm_client.py     ← Gemini API wrapper
"""

import os
import io
import csv
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from styles import MAIN_CSS
from utils  import _build_crm_entry, _entries_to_csv, _load_crm, _save_crm

load_dotenv()

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Sales Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "crm_entries" not in st.session_state:
    st.session_state["crm_entries"] = _load_crm()   # persist across refresh

for key, default in [
    ("proposal",         None),
    ("client_data",      None),
    ("proposal_history", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════
with st.sidebar:
    # Brand block
    # st.markdown("""
    # <div style='background:linear-gradient(135deg,#0C1320,#111D35);
    # border:1px solid #1E2840;border-radius:12px;padding:1.2rem 1.3rem;margin-bottom:1.4rem;'>
    #   <div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:#EEF2FF;'>
    #     ⚡ AI Sales Intelligence</div>
    #   <div style='font-size:.75rem;color:#3D4D66;margin-top:.25rem;'>
    #     RAG + Gemini + FAISS · v2</div>
    # </div>
    # """, unsafe_allow_html=True)

    # st.markdown("### ⚙️ Configuration")

    default_key = os.getenv("GEMINI_API_KEY", "")
    if default_key and default_key != "your_gemini_api_key_here":
        gemini_key = default_key
        # st.success("✅ API Key loaded from .env")
    else:
        gemini_key = st.text_input("Gemini API Key", type="password",
                                   help="Get free key at aistudio.google.com")

    model_choice = st.selectbox("LLM Model",
        ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"], index=0)
    os.environ["GEMINI_MODEL"] = model_choice

    st.markdown("---")
    st.markdown("### 🧠 RAG Settings")
    top_k      = st.slider("Similar Proposals (k)", 1, 5, 2)
    use_filter = st.checkbox("Industry Filter", value=True,
                             help="Only retrieve proposals from same industry")

    st.markdown("---")
    st.markdown("### 🗄️ Vector DB")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🌱 Seed"):
            if not gemini_key:
                st.warning("Add API key first!")
            else:
                with st.spinner("Seeding 8 proposals..."):
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

    # CRM exports
    _n = len(st.session_state["crm_entries"])
    if _n > 0:
        st.markdown("---")
        st.markdown(f"### 📊 CRM ({_n} lead{'s' if _n!=1 else ''})")
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

    # Session history
    if st.session_state["proposal_history"]:
        st.markdown("---")
        st.markdown("### 📚 Session History")
        for i, h in enumerate(reversed(st.session_state["proposal_history"][-5:])):
            if st.button(f"📄 {h['company']}  ·  {h['roi']}% ROI", key=f"hist_{i}"):
                st.session_state["proposal"]    = h["proposal"]
                st.session_state["client_data"] = h["client"]
                st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:.78rem;color:#3D4D66;line-height:2;'>
    <b style='color:#7B88A0;'>Prerequisites: LLM</b><br>
    🤖 Gemini 2.5 Flash<br>
    🔍 FAISS Vector Search<br>
    🧮 sentence-transformers<br>
    🐍 Python 3.10+<br>
    🖥️ Streamlit
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════
_n  = len(st.session_state["crm_entries"])
_wt = sum(e["deal"].get("weighted_value", 0) for e in st.session_state["crm_entries"])

st.markdown(f"""
<div class="hero-wrap"><

  <div class="hero-title">AI Sales <span class="hl">Proposal Generator  </span>& CRM Auto-Updater</div>

  
  
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# WORKFLOW STEPS BAR
# ════════════════════════════════════════════════════════
st.markdown("""
<div class="steps-wrap">
  <div class="step">
    <div class="step-num active">1</div>
    <div class="step-info">
      <div class="sn active">Client Info</div>
      <div class="sd">Input</div>
    </div>
  </div>
  <div class="step-line"></div>
  <div class="step">
    <div class="step-num">2</div>
    <div class="step-info">
      <div class="sn">AI Proposal</div>
      <div class="sd">Generation</div>
    </div>
  </div>
  <div class="step-line"></div>
  <div class="step">
    <div class="step-num">3</div>
    <div class="step-info">
      <div class="sn">Pricing</div>
      <div class="sd">Options</div>
    </div>
  </div>
  <div class="step-line"></div>
  <div class="step">
    <div class="step-num">4</div>
    <div class="step-info">
      <div class="sn">Follow-up</div>
      <div class="sd">Email Draft</div>
    </div>
  </div>
  <div class="step-line"></div>
  <div class="step">
    <div class="step-num">5</div>
    <div class="step-info">
      <div class="sn">CRM</div>
      <div class="sd">Auto-Update</div>
    </div>
  </div>
  <div class="step-line"></div>
  <div class="step">
    <div class="step-num">6</div>
    <div class="step-info">
      <div class="sn">JSON/CSV</div>
      <div class="sd">Export</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# MAIN TABS  (static labels — no tab reset bug)
# ════════════════════════════════════════════════════════
tab_gen, tab_crm = st.tabs(["🚀 Generate Proposal", "🗂️ CRM Dashboard"])


# ════════════════════════════════════════════════════════
# TAB 1 — GENERATE PROPOSAL
# ════════════════════════════════════════════════════════
with tab_gen:

    # ── Client Form ──────────────────────────────────────────────────────────
    st.markdown('<div class="sec-label">📋 Step 1 Client Details</div>',
                unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        company_name = st.text_input("Client / Company Name *",
                                     placeholder="e.g. HealthAI Solutions Ltd.")
        industry     = st.selectbox("Sector / Industry *", [
            "Healthcare", "Fintech", "E-commerce", "SaaS", "EdTech",
            "Logistics", "Manufacturing", "Real Estate", "LegalTech", "Other"
        ])
        team_size   = st.number_input("Team Size", min_value=1, value=50, step=10)
        current_rev = st.number_input("Current Annual Revenue ($)", min_value=0,
                                       value=2_000_000, step=100_000, format="%d")
    with r1c2:
        goals = st.text_area("Business Goals *",
            placeholder="e.g. Automate 70% of workflows, reduce CAC by 40%, scale to 10x users...",
            height=130)
        budget_min = st.number_input("Budget Min ($)", min_value=10_000,
                                      value=100_000, step=10_000, format="%d")
        budget_max = st.number_input("Budget Max ($)", min_value=10_000,
                                      value=500_000, step=10_000, format="%d")
        timeline   = st.slider("Engagement Duration (months)", 3, 24, 12)

    problem = st.text_area("Client Requirements / Problem Statement *",
        placeholder="e.g. Patient onboarding takes 3x industry average. Manual workflows cost 4 hrs/staff/day...",
        height=100)

    # ── Generate Button ───────────────────────────────────────────────────────
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    gen_btn = st.button("🚀 Generate AI-Powered Proposal + Auto-Update CRM",
                        use_container_width=True)

    if gen_btn:
        # Validate
        if not gemini_key or gemini_key == "your_gemini_api_key_here":
            st.error("⚠️ Add your Gemini API key in the sidebar or .env file.")
            st.stop()
        if not company_name:
            st.error("⚠️ Company Name is required.")
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
        status       = st.status("Initializing pipeline...", expanded=True)

        try:
            with status:
                st.write("🔧 Loading Gemini client and RAG engine...")
                progress_bar.progress(10)
                from proposal_generator import ProposalGenerator
                gen = ProposalGenerator(api_key=gemini_key)

                st.write(f"🔍 Searching FAISS for similar {industry} proposals...")
                progress_bar.progress(25)

                st.write("🤖 Generating proposal with Gemini 2.5 Flash...")
                progress_bar.progress(45)
                proposal = gen.generate(client_data, k=top_k, filters=filters)

                st.write("✅ Validating JSON + math (ROI / payback)...")
                progress_bar.progress(75)

                st.write("📧 Generating follow-up email...")
                progress_bar.progress(88)

                st.write("💾 Storing in FAISS + auto-updating CRM...")
                progress_bar.progress(100)

            status.update(label="✅ Proposal generated! CRM auto-updated.", state="complete")

            # Save proposal to session
            st.session_state["proposal"]    = proposal
            st.session_state["client_data"] = client_data

            # Auto-add to CRM
            crm_entry = _build_crm_entry(proposal, client_data)
            existing  = [e for e in st.session_state["crm_entries"]
                         if e["lead_info"]["name"].lower() != company_name.strip().lower()]
            existing.insert(0, crm_entry)
            st.session_state["crm_entries"] = existing
            _save_crm(existing)

            # Add to history
            st.session_state["proposal_history"].append({
                "company":  company_name,
                "industry": industry,
                "roi":      proposal.get("roi_percentage", "N/A"),
                "inv":      proposal.get("total_investment", 0),
                "time":     datetime.now().strftime("%H:%M"),
                "proposal": proposal,
                "client":   client_data,
            })
            st.balloons()

        except Exception as e:
            err = str(e).lower()
            if "quota" in err or "429" in err or "rate" in err:
                status.update(label="❌ API quota exceeded", state="error")
                st.error("⚠️ Rate limit hit. Wait 30s or switch to gemini-2.0-flash in sidebar.")
            elif "api key" in err or "invalid" in err or "permission" in err:
                status.update(label="❌ Invalid API key", state="error")
                st.error("⚠️ Invalid API key. Check at aistudio.google.com")
            elif "json" in err or "parse" in err:
                status.update(label="❌ JSON parse error", state="error")
                st.error("⚠️ Response parsing failed. Try again.")
            else:
                status.update(label="❌ Error", state="error")
                st.error(f"Generation failed: {e}")
            st.info("💡 Tip: Seed demo data from sidebar Vector DB section before generating.")

    # ── Results section ───────────────────────────────────────────────────────
    if st.session_state["proposal"] and st.session_state["client_data"]:
        p  = st.session_state["proposal"]
        cd = st.session_state["client_data"]

        st.markdown("<hr style='border-color:#1E2840;margin:2rem 0;'>", unsafe_allow_html=True)

        # Header row
        st.markdown(f"""
        <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:1.2rem;'>
          <div>
            <span style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#EEF2FF;'>
              📄 {cd["company_name"]}</span>
            <span style='margin-left:.9rem;font-size:.85rem;color:#7B88A0;'>
              {cd["industry"]}  ·  {datetime.now():%d %b %Y}</span>
          </div>
          <span style='background:rgba(0,229,180,.1);color:#00E5B4;
          border:1px solid rgba(0,229,180,.3);font-size:.75rem;font-weight:700;
          padding:.3rem .85rem;border-radius:50px;'>✅ Auto-saved to CRM</span>
        </div>
        """, unsafe_allow_html=True)

        # Info bar
        rag_count  = p.get("_rag_count", 0)
        math_check = p.get("_roi_math_check", "")
        st.markdown(f"""
        <div class="info-bar">
          <span>🔍 <strong>RAG Active</strong> — {rag_count} similar proposal(s) used</span>
          <span style='color:#1E2840;'>|</span>
          <span>🤖 <strong>{model_choice}</strong></span>
          <span style='color:#1E2840;'>|</span>
          <span>✅ <strong>JSON Validated</strong></span>
          <span style='color:#1E2840;'>|</span>
          <span>♻️ <strong>Stored in FAISS</strong></span>
          <span style='color:#1E2840;'>|</span>
          <span>📊 <strong>CRM Updated</strong></span>
        </div>
        {"<div class='math-bar'>📐 ROI Verified: " + math_check + "</div>" if math_check else ""}
        """, unsafe_allow_html=True)

        # KPI strip
        inv       = p.get("total_investment", 0)
        roi       = p.get("roi_percentage", 0)
        total_rev = sum(p.get("monthly_revenue_projection", []))
        pb        = p.get("payback_period_months", "N/A")

        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(f'<div class="pk g"><div class="pk-val">{roi}%</div><div class="pk-lbl">Projected ROI</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="pk b"><div class="pk-val">${inv:,}</div><div class="pk-lbl">Total Investment</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="pk p"><div class="pk-val">${total_rev:,}</div><div class="pk-lbl">12-Month Revenue</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="pk a"><div class="pk-val">{pb} mo</div><div class="pk-lbl">Payback Period</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Inner tabs ──────────────────────────────────────────────────────
        t1, t2, t3, t4 = st.tabs([
            "📊 Proposal",
            "📧 Follow-up Email",
            "🔍 RAG Context",
            "📥 Downloads",
        ])

        # ══ TAB: PROPOSAL ══
        with t1:
            st.markdown('<div class="sec-t">💼 Executive Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="summary-box">{p.get("executive_summary","")}</div>',
                        unsafe_allow_html=True)

            st.markdown('<div class="sec-t">🔴 Problem Analysis</div>', unsafe_allow_html=True)
            pa = p.get("problem_analysis", {})
            if pa:
                col_p1, col_p2 = st.columns([3, 1])
                with col_p1:
                    for ch in pa.get("primary_challenges", []):
                        st.markdown(f'<div class="challenge-item">⚠️ {ch}</div>',
                                    unsafe_allow_html=True)
                with col_p2:
                    st.metric("Revenue Impact", pa.get("revenue_impact", "N/A"))

            st.markdown('<div class="sec-t">🗺️ Implementation Phases</div>', unsafe_allow_html=True)
            for i, phase in enumerate(p.get("proposed_solution", {}).get("phases", [])):
                with st.expander(
                    f"{phase.get('phase')} — {phase.get('name','')}  ·  {phase.get('duration','')}",
                    expanded=(i == 0)
                ):
                    for d in phase.get("key_deliverables", []):
                        st.markdown(f"✅ &nbsp; {d}")

            st.markdown('<div class="sec-t">📈 Monthly Revenue Projection</div>', unsafe_allow_html=True)
            rev_data = p.get("monthly_revenue_projection", [])
            if rev_data:
                import pandas as pd
                df = pd.DataFrame({
                    "Month": [f"M{i+1}" for i in range(len(rev_data))],
                    "Revenue ($)": rev_data
                }).set_index("Month")
                st.line_chart(df, height=260)
                with st.expander("📋 Monthly Breakdown"):
                    cols = st.columns(6)
                    for i, (r, col) in enumerate(zip(rev_data, cols * 2)):
                        col.metric(f"Month {i+1}", f"${r:,}")

            st.markdown('<div class="sec-t">💰 Budget Allocation</div>', unsafe_allow_html=True)
            ba = p.get("budget_allocation", {})
            if ba:
                b_cols = st.columns(len(ba))
                for (cat, pct), col in zip(ba.items(), b_cols):
                    col.metric(cat.upper(), f"{pct}%", f"${int(inv * pct / 100):,}")

            st.markdown('<div class="sec-t">⭐ Why Choose Us</div>', unsafe_allow_html=True)
            for point in p.get("why_us", []):
                st.markdown(f"✦ &nbsp; {point}")

            st.markdown('<div class="sec-t">🚀 Next Steps</div>', unsafe_allow_html=True)
            st.info(p.get("next_steps", ""))

        # ══ TAB: EMAIL ══
        with t2:
            email_raw = p.get("_followup_email", "")
            if email_raw:
                lines   = email_raw.strip().split("\n")
                subject = next((l.split(":", 1)[1].strip() for l in lines
                                if l.lower().startswith("subject:")), "")
                body    = "\n".join(l for l in lines
                                    if not l.lower().startswith("subject:")).strip()
                if subject:
                    st.markdown(f"""
                    <div class="subj-bar">
                      <div class="lbl">Subject Line</div>
                      <div class="val">{subject}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f'<div class="email-box">{body}</div>', unsafe_allow_html=True)
                st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
                ec1, ec2 = st.columns(2)
                with ec1:
                    st.text_area("✏️ Edit before sending", value=body,
                                 height=200, key="email_edit")
                with ec2:
                    st.download_button("📋 Download Email (.txt)", data=email_raw,
                        file_name=f"followup_{cd['company_name'].replace(' ','_')}.txt",
                        mime="text/plain", use_container_width=True)
            else:
                st.info("Follow-up email not generated. Check logs or try regenerating.")

        # ══ TAB: RAG CONTEXT ══
        with t3:
            rag_sources = p.get("_rag_sources", [])
            if rag_sources:
                st.markdown(f"""
                <div class="rag-hdr">
                  🔍 <strong>{len(rag_sources)} proposal(s)</strong> retrieved from FAISS vector store
                  and injected as context into Gemini prompt — making proposals industry-specific and grounded.
                </div>
                """, unsafe_allow_html=True)
                for src in rag_sources:
                    score_pct = int(src["score"] * 100)
                    cls       = "hi" if score_pct >= 70 else "md" if score_pct >= 45 else "lo"
                    bar_clr   = "#00E5B4" if cls=="hi" else "#FFB84D" if cls=="md" else "#3D4D66"
                    st.markdown(f"""
                    <div class="rag-card">
                      <div class="rag-top">
                        <div>
                          <span class="rag-co">{src['company']}</span>
                          <span class="rag-ind">— {src['industry']}</span>
                        </div>
                        <span class="rag-badge {cls}">Similarity: {score_pct}%</span>
                      </div>
                      <div class="rag-nums">
                        <span>ROI: {src['roi']}%</span>
                        <span>Budget: ${src['budget']:,}</span>
                      </div>
                      <div class="rag-bar">
                        <div class="rag-bar-fill" style="width:{score_pct}%;background:{bar_clr};"></div>
                      </div>
                      <div class="rag-quote">"{src['summary']}"</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("#### 🔬 How RAG Works in This Pipeline")
                st.markdown("""
1. **Your query** → sentence-transformers converts to 384-dim vector
2. **FAISS search** → finds nearest neighbors by cosine similarity
3. **Retrieved docs** → top-k injected into Gemini prompt as context
4. **Gemini generates** → using real past data, not hallucination
5. **Stored back** → this proposal added to FAISS for future use *(continuous learning)*
                """)
            else:
                st.warning("No similar proposals retrieved from FAISS.")
                st.info("💡 Click **🌱 Seed** in the sidebar to add 8 sample proposals, then regenerate.")

        # ══ TAB: DOWNLOADS ══
        with t4:
            st.markdown('<div class="sec-t">⬇️ Download Everything</div>', unsafe_allow_html=True)
            dl1, dl2, dl3 = st.columns(3)
            with dl1:
                st.download_button("📦 Full Proposal JSON",
                    data=json.dumps({"client": cd, "proposal": {
                        k: v for k, v in p.items() if not k.startswith("_")
                    }}, indent=2, ensure_ascii=False),
                    file_name=f"proposal_{cd['company_name'].replace(' ','_')}.json",
                    mime="application/json", use_container_width=True)
            with dl2:
                st.download_button("🧹 Clean Proposal JSON",
                    data=json.dumps({k: v for k, v in p.items() if not k.startswith("_")},
                                    indent=2, ensure_ascii=False),
                    file_name=f"clean_{cd['company_name'].replace(' ','_')}.json",
                    mime="application/json", use_container_width=True)
            with dl3:
                st.download_button("📧 Follow-up Email (.txt)",
                    data=p.get("_followup_email", "No email generated."),
                    file_name=f"email_{cd['company_name'].replace(' ','_')}.txt",
                    mime="text/plain", use_container_width=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown("#### 👁️ Proposal JSON Preview")
            st.json({k: v for k, v in p.items() if not k.startswith("_")})


# ════════════════════════════════════════════════════════
# TAB 2 — CRM DASHBOARD
# ════════════════════════════════════════════════════════
with tab_crm:
    entries = st.session_state["crm_entries"]   # always fresh read
    n_crm   = len(entries)

    if not entries:
        st.markdown("""
        <div style='text-align:center;padding:5rem 2rem;'>
          <div style='font-size:4rem;margin-bottom:1rem;'>📊</div>
          <div style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#EEF2FF;'>
            CRM is empty</div>
          <div style='font-size:.98rem;color:#7B88A0;max-width:420px;
          margin:.6rem auto 0;line-height:1.7;'>
          Go to <strong style='color:#EEF2FF;'>🚀 Generate Proposal</strong> tab →
          fill the form → click <strong style='color:#00E5B4;'>Generate</strong>.<br><br>
          Every proposal auto-saves here and persists across sessions.
          </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        total_wt = sum(e["deal"].get("weighted_value", 0) for e in entries)
        n_won    = len([e for e in entries if e["deal"]["stage"] == "Closed Won"])
        win_rate = round(n_won / n_crm * 100) if n_crm else 0
        avg_roi  = round(sum(e["proposal_metadata"].get("roi", 0) for e in entries) / n_crm)

        # ── Header ──────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="crm-hdr">
          <div>
            <div class="crm-hdr-title">📊 CRM Dashboard</div>
            <div class="crm-hdr-sub">
              Auto-updated · {n_crm} lead{"s" if n_crm!=1 else ""} · {datetime.now():%d %b %Y, %H:%M}
            </div>
          </div>
          <div>
            <div class="crm-hdr-count">{n_crm}</div>
            <div class="crm-hdr-lbl">Leads in Pipeline</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPI Strip ───────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="kpi-row">
          <div class="kb">
            <div class="bar" style="background:#4D9EFF;"></div>
            <div class="kv">{n_crm}</div>
            <div class="kl">Total Leads</div>
            <div class="ks">All proposals sent</div>
          </div>
          <div class="kb">
            <div class="bar" style="background:#00E5B4;"></div>
            <div class="kv">{n_won}</div>
            <div class="kl">Closed Won</div>
            <div class="ks">Converted deals</div>
          </div>
          <div class="kb">
            <div class="bar" style="background:#FFB84D;"></div>
            <div class="kv">{win_rate}%</div>
            <div class="kl">Win Rate</div>
            <div class="ks">Closed / Total</div>
          </div>
          <div class="kb">
            <div class="bar" style="background:#9B7BFF;"></div>
            <div class="kv">${total_wt:,}</div>
            <div class="kl">Weighted Pipeline</div>
            <div class="ks">Probability adjusted</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Industry Chart ──────────────────────────────────────────────────
        import pandas as pd
        ind_map = {}
        for e in entries:
            ind = e["lead_info"]["industry"]
            ind_map[ind] = ind_map.get(ind, 0) + 1
        if len(ind_map) >= 2:
            st.markdown('<div class="crm-sec">🏭 Leads by Industry</div>', unsafe_allow_html=True)
            df_i = pd.DataFrame({"Industry": list(ind_map.keys()),
                                 "Leads":    list(ind_map.values())}).set_index("Industry")
            st.bar_chart(df_i, height=170)

        # ── Filters ─────────────────────────────────────────────────────────
        st.markdown("<hr class='crm-div'>", unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filt_s = st.selectbox("Filter Stage",
                ["All","Proposal Sent","Qualified","Negotiation","Closed Won","Closed Lost"],
                key="crm_filt_s")
        with fc2:
            inds   = ["All"] + sorted({e["lead_info"]["industry"] for e in entries})
            filt_i = st.selectbox("Filter Industry", inds, key="crm_filt_i")
        with fc3:
            sort   = st.selectbox("Sort",
                ["Latest First","Highest ROI","Highest Value"], key="crm_sort")

        filtered = entries[:]
        if filt_s != "All":
            filtered = [e for e in filtered if e["deal"]["stage"] == filt_s]
        if filt_i != "All":
            filtered = [e for e in filtered if e["lead_info"]["industry"] == filt_i]
        if sort == "Highest ROI":
            filtered.sort(key=lambda x: x["proposal_metadata"].get("roi", 0), reverse=True)
        elif sort == "Highest Value":
            filtered.sort(key=lambda x: x["lead_info"].get("budget_num", 0), reverse=True)

        st.markdown(
            f'<div class="crm-sec">💼 All Leads '
            f'<span style="background:rgba(77,158,255,.15);color:#4D9EFF;'
            f'font-size:.7rem;font-weight:800;padding:.2rem .6rem;'
            f'border-radius:50px;margin-left:.4rem;">{len(filtered)}</span></div>',
            unsafe_allow_html=True
        )

        # Stage style map
        STAGE_STYLE = {
            "Proposal Sent": ("#FEF3C7","#92400E","#D97706"),
            "Qualified":     ("#D1FAE5","#065F46","#059669"),
            "Negotiation":   ("#FEE2E2","#991B1B","#EF4444"),
            "Closed Won":    ("#D1FAE5","#065F46","#059669"),
            "Closed Lost":   ("#F3F4F6","#374151","#6B7280"),
        }
        STAGE_PROB = {
            "Proposal Sent": 55, "Qualified": 30, "Negotiation": 75,
            "Closed Won": 100,   "Closed Lost": 0,
        }

        # ── Lead Cards ──────────────────────────────────────────────────────
        for idx, entry in enumerate(filtered):
            li    = entry["lead_info"]
            deal  = entry["deal"]
            meta  = entry.get("proposal_metadata", {})
            fu_e  = entry.get("follow_up_email", {})
            stage = deal.get("stage", "Proposal Sent")
            prob  = deal.get("probability", 55)
            wval  = deal.get("weighted_value", 0)
            sbg, sfg, sbrd = STAGE_STYLE.get(stage, ("#EFF6FF","#1E40AF","#2563EB"))

            try:
                orig_idx = st.session_state["crm_entries"].index(entry)
            except ValueError:
                orig_idx = idx

            with st.expander(
                f"🏢  {li['name']}  ·  {li['industry']}  ·  "
                f"{li.get('estimated_value','N/A')}  ·  {stage}",
                expanded=(idx == 0)
            ):
                # Metrics row
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("💰 Budget",      li.get("estimated_value","N/A"))
                m2.metric("📊 Probability", f"{prob}%")
                m3.metric("🎯 Weighted",    f"${wval:,}")
                m4.metric("📈 ROI",         f"{meta.get('roi',0)}%")

                # Stage pill + progress bar
                st.markdown(f"""
                <div style='margin:.7rem 0 .3rem;'>
                  <span class="stage-pill"
                    style="background:{sbg};color:{sfg};border:1px solid {sbrd};">{stage}</span>
                  <span style='font-size:.82rem;color:#7B88A0;margin-left:.75rem;'>
                    {prob}% probability · Payback: {meta.get('payback','N/A')} months</span>
                </div>
                <div class="prob-bar">
                  <div class="prob-fill" style="width:{prob}%;background:{sbrd};"></div>
                </div>
                """, unsafe_allow_html=True)

                # Summary
                summary = meta.get("summary","")
                if summary:
                    st.markdown(f'<div class="lead-sum">📝 {summary}</div>',
                                unsafe_allow_html=True)

                # Follow-up email preview
                if fu_e:
                    subj = fu_e.get("subject","") if isinstance(fu_e, dict) else ""
                    body = fu_e.get("body","")    if isinstance(fu_e, dict) else str(fu_e)
                    with st.expander("📧 Follow-up Email Draft"):
                        if subj:
                            st.markdown(f"**Subject:** {subj}")
                        body_clean = "\n".join(
                            l for l in body.split("\n")
                            if not l.lower().startswith("subject:")
                        ).strip()
                        st.markdown(f'<div class="email-box">{body_clean}</div>',
                                    unsafe_allow_html=True)

                # Stage updater + downloads
                st.markdown("<hr style='border-color:#1E2840;margin:1.2rem 0;'>",
                            unsafe_allow_html=True)
                sc1, sc2, sc3 = st.columns([3, 1, 1])

                with sc1:
                    stage_opts = ["Proposal Sent","Qualified","Negotiation","Closed Won","Closed Lost"]
                    cur_idx    = stage_opts.index(stage) if stage in stage_opts else 0
                    new_stage  = st.selectbox("Update Stage", stage_opts,
                                             index=cur_idx, key=f"crm_stage_{orig_idx}")
                    if st.button("✅ Update Stage", key=f"crm_upd_{orig_idx}"):
                        new_prob = STAGE_PROB.get(new_stage, 55)
                        st.session_state["crm_entries"][orig_idx]["deal"]["stage"]          = new_stage
                        st.session_state["crm_entries"][orig_idx]["lead_info"]["status"]    = new_stage
                        st.session_state["crm_entries"][orig_idx]["deal"]["probability"]    = new_prob
                        st.session_state["crm_entries"][orig_idx]["deal"]["weighted_value"] = int(
                            li.get("budget_num", 0) * new_prob / 100)
                        _save_crm(st.session_state["crm_entries"])
                        st.success(f"✅ Stage → {new_stage}")
                        st.rerun()

                with sc2:
                    st.download_button("📋 JSON",
                        data=json.dumps(entry, indent=2, ensure_ascii=False),
                        file_name=f"crm_{li['name'].replace(' ','_')}.json",
                        mime="application/json",
                        key=f"crm_dlj_{orig_idx}", use_container_width=True)
                with sc3:
                    buf = io.StringIO()
                    w   = csv.DictWriter(buf, fieldnames=[
                        "name","industry","budget","status","stage",
                        "probability","roi","payback","added_at"])
                    w.writeheader()
                    w.writerow({
                        "name":        li["name"],
                        "industry":    li["industry"],
                        "budget":      li.get("estimated_value",""),
                        "status":      li.get("status",""),
                        "stage":       deal["stage"],
                        "probability": deal["probability"],
                        "roi":         meta.get("roi",""),
                        "payback":     meta.get("payback",""),
                        "added_at":    li.get("added_at",""),
                    })
                    st.download_button("📊 CSV",
                        data=buf.getvalue().encode(),
                        file_name=f"crm_{li['name'].replace(' ','_')}.csv",
                        mime="text/csv",
                        key=f"crm_dlc_{orig_idx}", use_container_width=True)
