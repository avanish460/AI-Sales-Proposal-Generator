"""
styles.py — All CSS for AI Sales Intelligence Platform
Premium dark theme: large fonts, generous spacing, crisp hierarchy
"""

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg:        #080B10;
  --surf:      #0E1117;
  --surf2:     #141921;
  --surf3:     #1A2133;
  --bdr:       #1E2840;
  --bdr2:      #263350;
  --accent:    #00E5B4;
  --blue:      #4D9EFF;
  --purple:    #9B7BFF;
  --amber:     #FFB84D;
  --red:       #FF5C7A;
  --t1:        #EEF2FF;
  --t2:        #7B88A0;
  --t3:        #3D4D66;
--fd: 'Plus Jakarta Sans', sans-serif;
--fb: 'DM Sans', sans-serif;
--fm: 'Fira Code', monospace;
  --r:         12px;
  --r2:        8px;
}

html, body, [class*="css"], .stApp {
  font-family: var(--fb) !important;
  background: var(--bg) !important;
  color: var(--t1) !important;
  font-size: 15px !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.8rem 4rem !important; max-width: 1380px !important; }

/* ── HERO ── */
.hero-wrap {
  position: relative;
  background: linear-gradient(135deg, #0A0F1A 0%, #0D1525 60%, #111D35 100%);
  border: 1px solid var(--bdr2);
  border-radius: 18px;
  padding: 3rem 3.2rem 2.6rem;
  margin-bottom: 2rem;
  overflow: hidden;
}
.hero-wrap::before {
  content: '';
  position: absolute; top: -120px; right: -80px;
  width: 450px; height: 450px;
  background: radial-gradient(circle, rgba(0,229,180,.1) 0%, transparent 65%);
  pointer-events: none;
}
.hero-wrap::after {
  content: '';
  position: absolute; bottom: -80px; left: 200px;
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(77,158,255,.08) 0%, transparent 65%);
  pointer-events: none;
}
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: .5rem;
  background: rgba(0,229,180,.08);
  border: 1px solid rgba(0,229,180,.25);
  border-radius: 50px;
  padding: .32rem 1rem;
  font-size: .75rem; font-weight: 700;
  color: var(--accent); letter-spacing: .1em;
  text-transform: uppercase; margin-bottom: 1.1rem;
}
.hero-title {
  font-family: var(--fd) !important;
  font-size: 3rem !important;
  font-weight: 800 !important;
  color: var(--t1) !important;
  line-height: 1.8 !important;
  margin: 0 0 .8rem !important;
  letter-spacing: -.04em !important;
}
.hero-title .hl { color: var(--accent); }
.hero-sub {
  font-size: 1.05rem; color: var(--t2);
  line-height: 1.7; max-width: 540px; margin-bottom: 1.6rem;
}
.hero-sub strong { color: var(--t1); font-weight: 600; }
.hero-stats {
  position: absolute; top: 3rem; right: 3.2rem;
  display: flex; gap: 2.2rem;
}
.hero-stat-val {
  font-family: var(--fm);
  font-size: 2rem; font-weight: 600; color: var(--accent); line-height: 1;
}
.hero-stat-lbl {
  font-size: .65rem; color: var(--t3);
  text-transform: uppercase; letter-spacing: .12em;
  font-weight: 700; margin-top: .3rem;
}
.hero-chips { display: flex; flex-wrap: wrap; gap: .5rem; }
.hero-chip {
  background: rgba(255,255,255,.05);
  border: 1px solid var(--bdr2);
  border-radius: 50px;
  padding: .32rem .9rem;
  font-size: .78rem; font-weight: 500; color: var(--t2);
}

/* ── STEPS BAR ── */
.steps-wrap {
  background: var(--surf);
  border: 1px solid var(--bdr);
  border-radius: var(--r);
  padding: 1.1rem 1.8rem;
  margin-bottom: 2rem;
  display: flex; align-items: center; overflow-x: auto;
}
.step { display: flex; align-items: center; gap: .6rem; flex-shrink: 0; }
.step-num {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: .8rem; font-weight: 800;
  background: var(--surf2); border: 1.5px solid var(--bdr2); color: var(--t3);
}
.step-num.active { background: rgba(0,229,180,.15); border-color: var(--accent); color: var(--accent); }
.step-info { font-size: .78rem; line-height: 1.35; }
.step-info .sn { font-weight: 700; color: var(--t3); }
.step-info .sn.active { color: var(--t1); }
.step-info .sd { font-size: .7rem; color: var(--t3); }
.step-line { flex: 1; min-width: 28px; height: 1px; background: var(--bdr2); margin: 0 .8rem; }

/* ── SECTION HEADING ── */
.sec-label {
  font-size: .72rem; font-weight: 800; color: var(--accent);
  text-transform: uppercase; letter-spacing: .14em;
  margin: 2.4rem 0 1.4rem;
  display: flex; align-items: center; gap: .6rem;
}
.sec-label::after {
  content: ''; flex: 1; height: 1px;
  background: linear-gradient(to right, var(--bdr2), transparent);
}

/* ── INPUTS ── */
.stTextInput input, .stTextArea textarea {
  background: var(--surf) !important;
  border: 1.5px solid var(--bdr2) !important;
  border-radius: var(--r2) !important;
  color: var(--t1) !important;
  font-family: var(--fb) !important;
  font-size: 1rem !important;
  padding: .8rem 1.1rem !important;
  transition: border-color .15s, box-shadow .15s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(0,229,180,.12) !important;
}
.stTextInput label p, .stTextArea label p,
.stSelectbox label p, .stSlider label p,
.stNumberInput label p {
  color: var(--t2) !important;
  font-size: .75rem !important; font-weight: 700 !important;
  text-transform: uppercase !important; letter-spacing: .1em !important;
}
.stSelectbox > div > div {
  background: var(--surf) !important;
  border: 1.5px solid var(--bdr2) !important;
  border-radius: var(--r2) !important;
  color: var(--t1) !important; font-size: 1rem !important;
}
.stNumberInput > div {
  background: var(--surf) !important;
  border: 1.5px solid var(--bdr2) !important;
  border-radius: var(--r2) !important;
}
.stNumberInput input { font-size: 1rem !important; }
.stNumberInput button { background: var(--surf2) !important; color: var(--t2) !important; }
.stSlider > div > div > div { background: var(--accent) !important; }
.stCheckbox label p { color: var(--t2) !important; font-size: .9rem !important; }

/* ── GENERATE BUTTON ── */
.stButton > button {
  background: linear-gradient(135deg, #00C896, #00E5B4) !important;
  color: #080B10 !important; border: none !important;
  border-radius: var(--r) !important;
  padding: 1rem 2rem !important;
  font-family: var(--fd) !important;
  font-size: 1.05rem !important; font-weight: 800 !important;
  letter-spacing: .01em !important; width: 100% !important;
  box-shadow: 0 0 28px rgba(0,229,180,.22) !important;
  transition: all .2s !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 0 40px rgba(0,229,180,.38) !important;
}
.stDownloadButton > button {
  background: var(--surf2) !important; color: var(--t1) !important;
  border: 1.5px solid var(--bdr2) !important;
  border-radius: var(--r2) !important;
  font-size: .92rem !important; font-weight: 600 !important;
  padding: .65rem 1rem !important;
}
.stDownloadButton > button:hover {
  border-color: var(--accent) !important; color: var(--accent) !important;
}

/* ── TABS ── */
.stTabs [data-testid="stTabsBar"] {
  background: var(--surf) !important;
  border-bottom: 1px solid var(--bdr) !important;
  padding: 0 .5rem !important;
}
.stTabs [role="tab"] {
  font-family: var(--fb) !important;
  font-size: .92rem !important; font-weight: 600 !important;
  color: var(--t3) !important;
  padding: .9rem 1.4rem !important;
  border-bottom: 2px solid transparent !important;
}
.stTabs [role="tab"]:hover { color: var(--t2) !important; }
.stTabs [role="tab"][aria-selected="true"] {
  color: var(--accent) !important;
  border-bottom: 2px solid var(--accent) !important;
  background: transparent !important;
}
.stTabs [data-testid="stTabsContent"] {
  background: var(--surf) !important;
  border: 1px solid var(--bdr) !important; border-top: none !important;
  border-radius: 0 0 var(--r) var(--r) !important;
  padding: 2.2rem 2rem !important;
}

/* ── KPI CARDS (proposal view) ── */
.pk { background: var(--surf2); border: 1px solid var(--bdr2); border-radius: var(--r); padding: 1.5rem 1.4rem; position: relative; overflow: hidden; }
.pk::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; }
.pk.g::before { background: var(--accent); }
.pk.b::before { background: var(--blue); }
.pk.p::before { background: var(--purple); }
.pk.a::before { background: var(--amber); }
.pk-val { font-family: var(--fm); font-size: 2.4rem; font-weight: 600; line-height: 1; margin-bottom: .4rem; }
.pk.g .pk-val { color: var(--accent); }
.pk.b .pk-val { color: var(--blue); }
.pk.p .pk-val { color: var(--purple); }
.pk.a .pk-val { color: var(--amber); }
.pk-lbl { font-size: .72rem; font-weight: 700; color: var(--t3); text-transform: uppercase; letter-spacing: .1em; }

/* ── INFO BAR ── */
.info-bar {
  background: rgba(0,229,180,.05);
  border: 1px solid rgba(0,229,180,.2);
  border-radius: var(--r2);
  padding: .85rem 1.2rem;
  font-size: .88rem; color: var(--accent);
  display: flex; flex-wrap: wrap; gap: .5rem 1.5rem;
  align-items: center; margin-bottom: 1.2rem;
}
.math-bar {
  background: rgba(74,222,128,.05);
  border: 1px solid rgba(74,222,128,.18);
  border-radius: var(--r2);
  padding: .55rem 1.1rem;
  font-size: .82rem; color: #4ADE80;
  font-family: var(--fm); margin-bottom: 1.2rem;
}

/* ── SECTION TITLE (inside tabs) ── */
.sec-t {
  font-family: var(--fd);
  font-size: 1.05rem; font-weight: 700; color: var(--t1);
  border-left: 3px solid var(--accent);
  padding-left: .85rem; margin: 2rem 0 1rem;
}

/* ── CONTENT BOXES ── */
.summary-box {
  background: var(--surf2); border: 1px solid var(--bdr2);
  border-left: 3px solid var(--accent); border-radius: var(--r);
  padding: 1.6rem 1.8rem;
  font-size: 1rem; line-height: 1.8; color: var(--t1);
}
.challenge-item {
  background: rgba(255,92,122,.07);
  border: 1px solid rgba(255,92,122,.2);
  border-left: 3px solid var(--red);
  border-radius: var(--r2);
  padding: .8rem 1.1rem; margin: .5rem 0;
  font-size: .93rem; color: #FFAAB8; line-height: 1.55;
}

/* ── EMAIL ── */
.email-box {
  background: var(--surf2); border: 1px solid var(--bdr2);
  border-left: 3px solid var(--blue); border-radius: var(--r);
  padding: 1.5rem 1.8rem;
  font-size: .95rem; line-height: 1.85; color: var(--t1); white-space: pre-wrap;
}
.subj-bar {
  background: rgba(77,158,255,.07);
  border: 1px solid rgba(77,158,255,.2);
  border-radius: var(--r2); padding: .8rem 1.2rem; margin-bottom: 1.1rem;
}
.subj-bar .lbl { font-size: .65rem; color: var(--t3); font-weight: 800; text-transform: uppercase; letter-spacing: .1em; }
.subj-bar .val { font-size: 1.05rem; color: var(--blue); font-weight: 700; margin-top: .2rem; }

/* ── RAG ── */
.rag-hdr {
  background: rgba(0,229,180,.06);
  border: 1px solid rgba(0,229,180,.2);
  border-radius: var(--r2); padding: .9rem 1.3rem;
  font-size: .92rem; color: var(--accent); margin-bottom: 1.3rem; line-height: 1.6;
}
.rag-card {
  background: var(--surf2); border: 1px solid var(--bdr2);
  border-radius: var(--r); padding: 1.2rem 1.5rem; margin: .7rem 0;
}
.rag-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: .7rem; }
.rag-co { font-size: 1rem; font-weight: 700; color: var(--t1); }
.rag-ind { font-size: .85rem; color: var(--t3); margin-left: .5rem; }
.rag-badge { font-family: var(--fm); font-size: .75rem; font-weight: 700; padding: .25rem .75rem; border-radius: 50px; }
.rag-badge.hi { background: rgba(0,229,180,.15); color: var(--accent); border: 1px solid rgba(0,229,180,.3); }
.rag-badge.md { background: rgba(255,184,77,.12); color: var(--amber); border: 1px solid rgba(255,184,77,.3); }
.rag-badge.lo { background: rgba(255,255,255,.05); color: var(--t3); border: 1px solid var(--bdr2); }
.rag-nums { display: flex; gap: 1.5rem; font-size: .88rem; color: var(--blue); font-weight: 600; margin-bottom: .6rem; }
.rag-bar { background: var(--bdr2); border-radius: 4px; height: 4px; margin-bottom: .65rem; }
.rag-bar-fill { height: 4px; border-radius: 4px; }
.rag-quote { font-size: .83rem; color: var(--t3); font-style: italic; line-height: 1.55; }

/* ── CRM DASHBOARD ── */
.crm-hdr {
  background: linear-gradient(135deg, #0C1320 0%, #101C35 100%);
  border: 1px solid var(--bdr2); border-radius: var(--r);
  padding: 1.8rem 2.2rem; margin-bottom: 1.6rem;
  display: flex; align-items: center; justify-content: space-between;
}
.crm-hdr-title { font-family: var(--fd); font-size: 1.4rem; font-weight: 800; color: var(--t1); }
.crm-hdr-sub { font-size: .85rem; color: var(--t3); margin-top: .3rem; }
.crm-hdr-count { font-family: var(--fm); font-size: 2.8rem; font-weight: 600; color: var(--accent); line-height: 1; text-align: right; }
.crm-hdr-lbl { font-size: .65rem; color: var(--t3); text-transform: uppercase; letter-spacing: .12em; font-weight: 700; }

.kpi-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 1.1rem; margin-bottom: 1.6rem; }
.kb {
  background: var(--surf2); border: 1px solid var(--bdr2);
  border-radius: var(--r); padding: 1.3rem 1.2rem;
  position: relative; overflow: hidden;
}
.kb .bar { position: absolute; top: 0; left: 0; width: 3px; height: 100%; border-radius: 14px 0 0 14px; }
.kb .kv { font-family: var(--fm); font-size: 2rem; font-weight: 600; color: var(--t1); padding-left: .65rem; line-height: 1.1; }
.kb .kl { font-size: .7rem; color: var(--t3); text-transform: uppercase; letter-spacing: .1em; font-weight: 700; margin: .3rem 0 0 .65rem; }
.kb .ks { font-size: .82rem; color: var(--t2); padding-left: .65rem; }

.crm-sec { font-size: .72rem; font-weight: 800; color: var(--t2); text-transform: uppercase; letter-spacing: .12em; margin: 1.6rem 0 .85rem; }
.crm-div { border: none; border-top: 1px solid var(--bdr); margin: 1.6rem 0; }

.lead-sum {
  background: var(--surf2); border: 1px solid var(--bdr2);
  border-left: 3px solid var(--blue); border-radius: var(--r2);
  padding: .9rem 1.2rem; margin: .9rem 0;
  font-size: .9rem; color: var(--t2); line-height: 1.6;
}
.stage-pill { display: inline-block; font-size: .75rem; font-weight: 700; padding: .25rem .8rem; border-radius: 50px; }
.prob-bar { background: var(--bdr2); border-radius: 4px; height: 5px; margin-top: .5rem; }
.prob-fill { height: 5px; border-radius: 4px; }
.tier-c {
  background: var(--surf); border: 1px solid var(--bdr2);
  border-radius: var(--r2); padding: 1rem 1.1rem;
}
.tier-c .tname { font-weight: 700; font-size: .93rem; color: var(--t1); margin-bottom: .4rem; }
.tier-c .tdesc { color: var(--t2); font-size: .85rem; line-height: 1.55; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] { background: var(--surf) !important; border-right: 1px solid var(--bdr) !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] div,
[data-testid="stSidebar"] .stMarkdown { color: var(--t1) !important; }
[data-testid="stSidebar"] h3 { font-family: var(--fd) !important; color: var(--accent) !important; font-weight: 700 !important; font-size: 1rem !important; }
[data-testid="stSidebar"] .stSelectbox > div > div { background: var(--surf2) !important; border-color: var(--bdr2) !important; color: var(--t1) !important; }
[data-testid="stSidebar"] .stTextInput input { background: var(--surf2) !important; border-color: var(--bdr2) !important; color: var(--t1) !important; }
[data-testid="stSidebar"] .stButton > button {
  background: var(--surf2) !important; color: var(--accent) !important;
  border: 1px solid rgba(0,229,180,.3) !important;
  box-shadow: none !important; font-size: .88rem !important;
  padding: .65rem 1rem !important; font-family: var(--fb) !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(0,229,180,.1) !important; transform: none !important; box-shadow: none !important;
}

/* ── ALERTS ── */
.stSuccess { background: rgba(0,229,180,.07) !important; border: 1px solid rgba(0,229,180,.25) !important; border-radius: var(--r2) !important; }
.stSuccess p { color: var(--accent) !important; font-size: .95rem !important; }
.stError { background: rgba(255,92,122,.07) !important; border: 1px solid rgba(255,92,122,.25) !important; border-radius: var(--r2) !important; }
.stError p { color: #FFAAB8 !important; font-size: .95rem !important; }
.stInfo { background: rgba(77,158,255,.07) !important; border: 1px solid rgba(77,158,255,.25) !important; border-radius: var(--r2) !important; }
.stInfo p { color: #93C5FD !important; font-size: .95rem !important; }
.stWarning { background: rgba(255,184,77,.07) !important; border: 1px solid rgba(255,184,77,.25) !important; border-radius: var(--r2) !important; }
.stWarning p { color: var(--amber) !important; font-size: .95rem !important; }

/* ── EXPANDERS ── */
[data-testid="stExpander"] { background: var(--surf2) !important; border: 1px solid var(--bdr2) !important; border-radius: var(--r) !important; }
[data-testid="stExpander"] summary { font-weight: 600 !important; color: var(--t1) !important; font-size: .95rem !important; }
[data-testid="stExpander"] summary:hover { color: var(--accent) !important; }

/* ── METRICS ── */
[data-testid="stMetricLabel"] p { color: var(--t3) !important; font-size: .72rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: .1em !important; }
[data-testid="stMetricValue"] { color: var(--t1) !important; font-family: var(--fm) !important; font-size: 1.5rem !important; font-weight: 600 !important; }

/* ── MISC ── */
hr { border-color: var(--bdr) !important; }
.stProgress > div { background: var(--bdr2) !important; border-radius: 4px !important; }
.stProgress > div > div { background: var(--accent) !important; border-radius: 4px !important; }
code { background: var(--surf2) !important; color: var(--accent) !important; border-radius: 4px !important; font-family: var(--fm) !important; }
</style>
"""
