"""
AI Sales Pro — Main App
Split into 3 files:
  app.py     ← you are here (UI logic)
  utils.py   ← PDF / CRM / CSV helpers
  styles.py  ← all CSS
"""

import json
import re
from datetime import datetime

import streamlit as st
import google.generativeai as genai

from utils  import (build_full_crm_entry, entries_to_csv,
                    create_pdf, load_crm, save_crm)
from styles import MAIN_CSS


# PROPOSAL RENDERER  
def _render_proposal(text: str, info: dict):
    """Parse proposal markdown and render as beautiful section cards."""

    SECTION_COLORS = {
        "executive summary":    ("blue",   "🎯"),
        "problem statement":    ("red",    "⚠️"),
        "proposed solution":    ("green",  "💡"),
        "why choose us":        ("purple", "⭐"),
        "implementation":       ("amber",  "📅"),
        "roi":                  ("green",  "📈"),
        "terms":                ("blue",   "📋"),
    }

    # Split on ## headings
    sections = re.split(r'\n(?=##+ )', text.strip())
    pricing_sections = {}
    main_sections    = []

    for sec in sections:
        lines   = sec.strip().splitlines()
        heading = lines[0].lstrip('#').strip() if lines else ""
        body    = "\n".join(lines[1:]).strip()

        if re.match(r'(basic|pro|enterprise)\s*(plan)?', heading, re.I):
            pricing_sections[heading] = body
        else:
            main_sections.append((heading, body))

    # ── Proposal header card ──
    st.markdown(f"""
    <div class="proposal-wrapper">
        <div class="proposal-header">
            <h2>📄 Proposal for {info.get('name','')}</h2>
            <span>{info.get('sector','')} · Generated {datetime.now():%d %b %Y}</span>
        </div>
        <div class="proposal-body">
    """, unsafe_allow_html=True)

    for heading, body in main_sections:
        if not heading:
            continue
        key    = heading.lower()
        color  = next((v[0] for k, v in SECTION_COLORS.items() if k in key), "blue")
        icon   = next((v[1] for k, v in SECTION_COLORS.items() if k in key), "📌")
        body_html = body.replace("\n", "<br>").replace("**", "")
        st.markdown(f"""
        <div class="p-section {color}">
            <h3>{icon} {heading}</h3>
            <p>{body_html}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Pricing cards (separate, prominent) ──
    if pricing_sections:
        st.markdown("<div style='margin-top:1.5rem;'><div class='section-h'>💰 Pricing Options</div>", unsafe_allow_html=True)
        st.markdown('<div class="pricing-grid">', unsafe_allow_html=True)
        for tier_name, tier_body in pricing_sections.items():
            css_cls = "pro" if "pro" in tier_name.lower() else (
                      "enterprise" if "enterprise" in tier_name.lower() else "basic")
            # badge   = '<div class="price-badge">⭐ Recommended</div>' if css_cls == "pro" else ""
            body_h  = tier_body.replace("\n", "<br>")
            st.markdown(f"""
            <div class="price-title">{tier_name}</div>
            <div class="price-desc">{body_h}</div>
            """, unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
# PAGE CONFIG
st.set_page_config(page_title="AI Sales Pro", layout="wide", page_icon="🚀")
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# GEMINI SETUP
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_OK = True
except Exception:
    GEMINI_OK = False

# SESSION STATE  (crm_entries loaded from disk on first run)
if "crm_entries" not in st.session_state:
    st.session_state["crm_entries"] = load_crm()        # ← persistent

for key, default in [
    ("last_proposal", None),
    ("last_followup", None),
    ("last_client",   {}),
    ("last_json",     None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# SIDEBAR

with st.sidebar:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1E3A5F,#2563EB);
    padding:1.1rem;border-radius:10px;margin-bottom:1rem;'>
        <div style='font-size:1.05rem;font-weight:800;color:#fff;'>🚀 AI Sales Pro</div>
        <div style='font-size:.72rem;color:rgba(255,255,255,.6);margin-top:.1rem;'>
        Proposal Generator + Auto CRM</div>
    </div>
    """, unsafe_allow_html=True)

    if not GEMINI_OK:
        st.error("⚠️ Add GEMINI_API_KEY to .streamlit/secrets.toml")
        st.code('[secrets]\nGEMINI_API_KEY = "AIzaSy..."', language="toml")

    st.markdown("### 📋 Client Details")
    client_name  = st.text_input("Client Name", placeholder="e.g. Acme Corp")
    sector       = st.selectbox("Industry Sector",
                    ["Technology","Healthcare","Finance","Retail","Manufacturing",
                     "EdTech","Logistics","Real Estate","Other"])
    budget       = st.text_input("Budget Range", placeholder="e.g. $5k – $10k")

    st.divider()
    requirements = st.text_area("Client Requirements",
                    placeholder="Describe what the client needs...", height=180)
    st.divider()

    # CRM export buttons (shown when data exists)
    if st.session_state["crm_entries"]:
        n = len(st.session_state["crm_entries"])
        st.markdown(f"### 📊 CRM  ({n} lead{'s' if n!=1 else ''})")
        all_json = json.dumps(st.session_state["crm_entries"], indent=2, ensure_ascii=False)
        st.download_button("📦 Export All JSON", data=all_json,
                           file_name="crm_all.json", mime="application/json",
                           use_container_width=True)
        st.download_button("📋 Export All CSV",
                           data=entries_to_csv(st.session_state["crm_entries"]),
                           file_name="crm_leads.csv", mime="text/csv",
                           use_container_width=True)
        if st.button("🗑️ Clear CRM", use_container_width=True):
            st.session_state["crm_entries"] = []
            save_crm([])
            st.rerun()

    st.markdown("""<div style='font-size:.78rem;color:#94A3B8;line-height:2;margin-top:.5rem;'>
    🤖 Gemini 2.5 Flash<br>📄 FPDF · JSON · CSV<br>☁️ Streamlit Cloud ready</div>""",
    unsafe_allow_html=True)


# TABS
n_crm = len(st.session_state["crm_entries"])
tab_gen, tab_crm = st.tabs([
    "⚡  Generate Proposal",
    f"📊  CRM Dashboard  {'🟢' if n_crm else '⚪'}  ({n_crm} leads)",
])


# TAB 1 — GENERATE PROPOSAL
with tab_gen:

    st.markdown("""
    <div class="hero">
        <h1>🚀 AI Sales Proposal Generator</h1>
        <p>Fill client details in the sidebar → AI generates proposal, email &amp; pricing — CRM auto-updates</p>
        <div class="hero-chips">
            <span class="hero-chip">📝 Full Proposal</span>
            <span class="hero-chip">💰 3 Pricing Tiers</span>
            <span class="hero-chip">📧 Follow-up Email</span>
            <span class="hero-chip">📄 PDF Download</span>
            <span class="hero-chip">📊 Auto CRM Update</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not GEMINI_OK:
        st.error("⚠️ Gemini API key missing! Add to `.streamlit/secrets.toml`")
        st.stop()

    gen_btn = st.button("✨ Generate Proposal + Auto-Update CRM", use_container_width=True)

    if gen_btn:
        if not client_name or not requirements:
            st.warning("⚠️ Please enter Client Name and Requirements.")
        else:
            prog = st.progress(0, text="Starting AI generation...")
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")

                # STEP 1 — Proposal
                prog.progress(10, text="📝 Drafting proposal...")
                proposal_prompt = f"""
You are an expert Sales Engineer in the {sector} industry.
Draft a formal, professional sales proposal for {client_name}.

Requirements to address: {requirements}
Budget context: {budget}

Structure your response EXACTLY like this (use these exact headings):

## Executive Summary
[2-3 compelling sentences]

## Problem Statement
[Client's pain points clearly articulated]

## Proposed Solution
[Detailed solution tailored to {sector}]

## Why Choose Us
[3 specific differentiators]

## Basic Plan
[Description and price]

## Pro Plan
[Description and price]

## Enterprise Plan
[Description and price]

## Implementation Timeline
[Phases with durations]

## ROI & Expected Outcomes
[Quantifiable benefits]

## Terms & Conditions
[Brief standard terms]
"""
                proposal_result = model.generate_content(proposal_prompt).text
                prog.progress(40, text="📧 Drafting follow-up email...")

                # STEP 2 — Email
                email_prompt = f"""
Write a short, professional follow-up email for this sales proposal.
Client: {client_name} | Industry: {sector} | Budget: {budget}
Key need: {requirements[:120]}

Rules:
- First line must be: Subject: [your subject here]
- Under 150 words
- Warm but professional tone
- Mention ONE specific pain point from the requirements
- Clear next step: schedule a 30-min discovery call
- End with: Best regards, [Your Name]

Write ONLY the email. Nothing else.
"""
                followup_email = model.generate_content(email_prompt).text
                prog.progress(75, text="📊 Updating CRM...")

                # STEP 3 — CRM
                crm_entry = build_full_crm_entry(
                    client_name, sector, budget, proposal_result, followup_email
                )
                existing = [e for e in st.session_state["crm_entries"]
                            if e["lead_info"]["name"].lower() != client_name.strip().lower()]
                existing.insert(0, crm_entry)
                st.session_state["crm_entries"]   = existing
                st.session_state["last_proposal"] = proposal_result
                st.session_state["last_followup"] = followup_email
                st.session_state["last_json"]     = json.dumps(crm_entry, indent=2, ensure_ascii=False)
                st.session_state["last_client"]   = {
                    "name": client_name, "sector": sector, "budget": budget
                }
                save_crm(existing)          # ← persist to disk

                prog.progress(100, text="✅ Done!")
                prog.empty()
                st.success(f"✅ Proposal generated! CRM auto-updated with **{client_name}**")
                st.balloons()

            except Exception as e:
                prog.empty()
                st.error(f"❌ An error occurred: {e}")

    # Results
    if st.session_state["last_proposal"]:
        p    = st.session_state["last_proposal"]
        fu   = st.session_state["last_followup"] or ""
        info = st.session_state["last_client"]
        jstr = st.session_state["last_json"] or ""

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:.75rem;'>
            <div>
                <span style='font-size:1.15rem;font-weight:800;color:#0F172A;'>
                📄 {info.get('name','')}</span>
                <span style='margin-left:.75rem;font-size:.78rem;color:#94A3B8;'>
                {info.get('sector','')} · {datetime.now():%d %b %Y}</span>
            </div>
            <span style='background:#ECFDF5;color:#059669;border:1px solid #6EE7B7;
            font-size:.73rem;font-weight:700;padding:.22rem .7rem;border-radius:20px;'>
            ✅ Auto-saved to CRM</span>
        </div>
        """, unsafe_allow_html=True)

        t1, t2, t3, t4 = st.tabs(["📝 Proposal", "📧 Follow-up Email", "📊 CRM JSON", "📥 Downloads"])

        #TAB: Proposal
        with t1:
            _render_proposal(p, info)

        #TAB: Follow-up Email
        with t2:
            if fu:
                lines     = fu.strip().split('\n')
                subject   = next((l.split(':',1)[1].strip() for l in lines
                                  if l.lower().startswith('subject:')), "")
                body_text = "\n".join(l for l in lines
                                      if not l.lower().startswith('subject:')).strip()
                if subject:
                    st.markdown(f"""
                    <div style='background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;
                    padding:.6rem 1rem;margin-bottom:.75rem;'>
                        <span style='color:#94A3B8;font-size:.68rem;font-weight:700;
                        text-transform:uppercase;letter-spacing:.06em;'>Subject Line</span><br>
                        <span style='color:#1E40AF;font-weight:700;font-size:.93rem;'>{subject}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f'<div class="email-box">{body_text}</div>', unsafe_allow_html=True)
                st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
                st.download_button("📋 Download Email (.txt)", data=fu,
                                   file_name=f"followup_{info.get('name','').replace(' ','_')}.txt",
                                   mime="text/plain")

        # TAB: CRM JSON
        with t3:
            st.markdown("""
            <div style='background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;
            padding:.6rem 1rem;margin-bottom:.75rem;font-size:.85rem;color:#1E40AF;font-weight:600;'>
            ℹ️ Full JSON entry — auto-saved to CRM Dashboard →
            </div>
            """, unsafe_allow_html=True)
            # Show JSON in scrollable box to prevent truncation
            st.markdown(f"""
            <div style='background:#0F172A;border-radius:10px;padding:1.2rem 1.4rem;
            max-height:520px;overflow-y:auto;font-family:JetBrains Mono,monospace;
            font-size:.78rem;line-height:1.7;color:#E2E8F0;white-space:pre-wrap;
            border:1px solid #1E293B;'>{jstr}</div>
            """, unsafe_allow_html=True)
            st.download_button("⬇️ Download Full JSON",
                               data=jstr,
                               file_name=f"{info.get('name','').replace(' ','_')}_CRM.json",
                               mime="application/json",
                               use_container_width=True)

        # TAB: Downloads
        with t4:
            st.markdown('<div class="section-h">⬇️ Download Everything</div>', unsafe_allow_html=True)
            d1, d2, d3 = st.columns(3)
            with d1:
                try:
                    pdf_file = create_pdf(p, info.get("name","Client"))
                    with open(pdf_file,"rb") as f:
                        st.download_button("📄 Download PDF Proposal", data=f,
                                           file_name=pdf_file, mime="application/pdf",
                                           use_container_width=True)
                except Exception as e:
                    st.warning(f"PDF generation issue: {e}")
            with d2:
                st.download_button("🔗 Export to CRM (JSON)", data=jstr,
                                   file_name=f"{info.get('name','').replace(' ','_')}_CRM.json",
                                   mime="application/json", use_container_width=True)
            with d3:
                st.download_button("📧 Download Email (.txt)", data=fu,
                                   file_name=f"followup_{info.get('name','').replace(' ','_')}.txt",
                                   mime="text/plain", use_container_width=True)


# TAB 2 — CRM DASHBOARD
with tab_crm:
    entries = st.session_state["crm_entries"]

    if not entries:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;'>
            <div style='font-size:3.5rem;margin-bottom:.8rem;'>📊</div>
            <div style='font-size:1.15rem;font-weight:800;color:#0F172A;'>CRM is empty</div>
            <div style='font-size:.9rem;color:#94A3B8;max-width:380px;margin:.5rem auto 0;line-height:1.6;'>
            Go to <strong>⚡ Generate Proposal</strong> tab →
            fill sidebar → click <strong>Generate Proposal + Auto-Update CRM</strong>.<br><br>
            Every proposal appears here automatically and persists across sessions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        total_val = sum(e["lead_info"].get("budget_num",0) for e in entries)
        total_wt  = sum(e["deal"].get("weighted_value",0) for e in entries)
        n_won     = len([e for e in entries if e["deal"]["stage"]=="Closed Won"])
        win_rate  = round(n_won / len(entries) * 100) if entries else 0

        # CRM header
        st.markdown(f"""
        <div class="crm-header">
            <div>
                <div style='font-size:1.15rem;font-weight:800;color:#fff;'>📊 CRM Dashboard</div>
                <div style='font-size:.78rem;color:rgba(255,255,255,.55);margin-top:.12rem;'>
                Persistent · {len(entries)} lead{"s" if len(entries)!=1 else ""} · {datetime.now():%d %b %Y, %H:%M}
                </div>
            </div>
            <div style='text-align:right;'>
                <div style='font-size:1.6rem;font-weight:800;color:#fff;
                font-family:JetBrains Mono,monospace;'>{len(entries)} Leads</div>
                <div style='font-size:.7rem;color:rgba(255,255,255,.5);'>in pipeline</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KPI strip
        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-box">
                <div class="bar" style="background:#2563EB;"></div>
                <div class="val">{len(entries)}</div>
                <div class="lbl">Total Leads</div>
                <div class="sub">All proposals sent</div>
            </div>
            <div class="kpi-box">
                <div class="bar" style="background:#059669;"></div>
                <div class="val">{n_won}</div>
                <div class="lbl">Closed Won</div>
                <div class="sub">Converted deals</div>
            </div>
            <div class="kpi-box">
                <div class="bar" style="background:#D97706;"></div>
                <div class="val">{win_rate}%</div>
                <div class="lbl">Win Rate</div>
                <div class="sub">Closed / Total</div>
            </div>
            <div class="kpi-box">
                <div class="bar" style="background:#4F46E5;"></div>
                <div class="val">${total_wt:,}</div>
                <div class="lbl">Weighted Pipeline</div>
                <div class="sub">Probability adjusted</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Industry chart
        import pandas as pd
        ind_map = {}
        for e in entries:
            ind = e["lead_info"]["industry"]
            ind_map[ind] = ind_map.get(ind, 0) + 1
        if len(ind_map) >= 2:
            st.markdown('<div class="section-h">🏭 Leads by Industry</div>', unsafe_allow_html=True)
            df_i = pd.DataFrame({"Industry": list(ind_map.keys()), "Leads": list(ind_map.values())}).set_index("Industry")
            st.bar_chart(df_i, height=160)

        # Filters
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filt_s = st.selectbox("Filter Stage",
                ["All","Proposal Sent","Qualified","Negotiation","Closed Won","Closed Lost"],
                key="filt_s")
        with fc2:
            inds   = ["All"] + sorted({e["lead_info"]["industry"] for e in entries})
            filt_i = st.selectbox("Filter Industry", inds, key="filt_i")
        with fc3:
            sort   = st.selectbox("Sort", ["Latest First","Highest Value"], key="crm_sort")

        filtered = entries[:]
        if filt_s != "All": filtered = [e for e in filtered if e["deal"]["stage"] == filt_s]
        if filt_i != "All": filtered = [e for e in filtered if e["lead_info"]["industry"] == filt_i]
        if sort == "Highest Value":
            filtered.sort(key=lambda x: x["lead_info"].get("budget_num", 0), reverse=True)

        # Lead cards
        st.markdown(f'<div class="section-h">💼 All Leads <span class="badge">{len(filtered)}</span></div>',
                    unsafe_allow_html=True)

        STAGE_STYLE = {
            "Proposal Sent": ("#FEF3C7","#92400E","#D97706"),
            "Qualified":     ("#D1FAE5","#065F46","#059669"),
            "Negotiation":   ("#FEE2E2","#991B1B","#EF4444"),
            "Closed Won":    ("#D1FAE5","#065F46","#059669"),
            "Closed Lost":   ("#F3F4F6","#374151","#6B7280"),
        }
        STAGE_PROB = {"Proposal Sent":55,"Qualified":30,"Negotiation":75,"Closed Won":100,"Closed Lost":0}

        import csv, io as _io

        for idx, entry in enumerate(filtered):
            li    = entry["lead_info"]
            deal  = entry["deal"]
            meta  = entry.get("proposal_metadata", {})
            fu_e  = entry.get("follow_up_email", {})
            price = entry.get("pricing_tiers", {})
            stage = deal.get("stage", "Proposal Sent")
            prob  = deal.get("probability", 55)
            wval  = deal.get("weighted_value", 0)
            sbg, sfg, sborder = STAGE_STYLE.get(stage, ("#EFF6FF","#1E40AF","#2563EB"))

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
                m4.metric("📅 Added",       li.get("added_at","")[:10])

                st.markdown(f"""
                <div style='margin:.6rem 0 .25rem;'>
                    <span style='background:{sbg};color:{sfg};border:1px solid {sborder};
                    font-size:.72rem;font-weight:700;padding:.2rem .7rem;border-radius:20px;'>
                    {stage}</span>
                    <span style='font-size:.78rem;color:#475569;margin-left:.65rem;font-weight:600;'>
                    {prob}% probability</span>
                </div>
                <div class="prog-bg">
                    <div class="prog-fill" style="width:{prob}%;background:{sborder};"></div>
                </div>
                """, unsafe_allow_html=True)

                summary = meta.get("summary","")
                if summary:
                    st.markdown(f"""
                    <div style='background:#F8FAFC;border:1px solid #E2E8F0;border-left:3px solid #2563EB;
                    border-radius:8px;padding:.7rem 1rem;margin:.7rem 0;
                    font-size:.85rem;color:#334155;line-height:1.6;'>📝 {summary}</div>
                    """, unsafe_allow_html=True)

                if price:
                    st.markdown("<p style='font-size:.74rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:.07em;margin:.7rem 0 .4rem;'>💰 Pricing Tiers</p>", unsafe_allow_html=True)
                    tier_bg = {"Basic":"#EFF6FF","Pro":"#F0FDF4","Enterprise":"#FEF3C7"}
                    pc = st.columns(len(price))
                    for (tier, desc), col in zip(price.items(), pc):
                        with col:
                            st.markdown(f"""
                            <div class="tier-card" style="background:{tier_bg.get(tier,'#F8FAFC')};">
                                <div style='font-weight:700;color:#0F172A;font-size:.85rem;margin-bottom:.3rem;'>{tier}</div>
                                <div style='color:#475569;font-size:.8rem;'>{desc[:200]}</div>
                            </div>
                            """, unsafe_allow_html=True)

                if fu_e:
                    subj = fu_e.get("subject","") if isinstance(fu_e, dict) else ""
                    body = fu_e.get("body","")    if isinstance(fu_e, dict) else str(fu_e)
                    with st.expander("📧 Follow-up Email Draft"):
                        if subj:
                            st.markdown(f"**Subject:** {subj}")
                        body_clean = "\n".join(l for l in body.split('\n')
                                               if not l.lower().startswith('subject:')).strip()
                        st.markdown(f'<div class="email-box">{body_clean}</div>', unsafe_allow_html=True)

                st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                sc1, sc2, sc3 = st.columns([3, 1, 1])

                with sc1:
                    stage_opts = ["Proposal Sent","Qualified","Negotiation","Closed Won","Closed Lost"]
                    cur_idx    = stage_opts.index(stage) if stage in stage_opts else 0
                    new_stage  = st.selectbox("Update Stage", stage_opts,
                                             index=cur_idx, key=f"stage_{orig_idx}")
                    if st.button("✅ Update Stage", key=f"upd_{orig_idx}"):
                        new_prob = STAGE_PROB.get(new_stage, 55)
                        st.session_state["crm_entries"][orig_idx]["deal"]["stage"]          = new_stage
                        st.session_state["crm_entries"][orig_idx]["lead_info"]["status"]    = new_stage
                        st.session_state["crm_entries"][orig_idx]["deal"]["probability"]    = new_prob
                        st.session_state["crm_entries"][orig_idx]["deal"]["weighted_value"] = int(
                            li.get("budget_num", 0) * new_prob / 100)
                        save_crm(st.session_state["crm_entries"])   # ← persist
                        st.success(f"✅ Stage → {new_stage}")
                        st.rerun()

                with sc2:
                    st.download_button(
                        "📋 JSON",
                        data=json.dumps(entry, indent=2, ensure_ascii=False),
                        file_name=f"crm_{li['name'].replace(' ','_')}.json",
                        mime="application/json",
                        key=f"dlj_{orig_idx}",
                        use_container_width=True
                    )
                with sc3:
                    buf = _io.StringIO()
                    w   = csv.DictWriter(buf, fieldnames=["name","industry","budget","status","stage","probability","added_at"])
                    w.writeheader()
                    w.writerow({"name":li["name"],"industry":li["industry"],
                                "budget":li.get("estimated_value",""),
                                "status":li["status"],"stage":deal["stage"],
                                "probability":deal["probability"],
                                "added_at":li.get("added_at","")})
                    st.download_button(
                        "📊 CSV",
                        data=buf.getvalue().encode(),
                        file_name=f"crm_{li['name'].replace(' ','_')}.csv",
                        mime="text/csv",
                        key=f"dlc_{orig_idx}",
                        use_container_width=True
                    )
