MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg:      #F7F9FC; --surface: #FFFFFF; --border: #E2E8F0;
    --t1:      #0F172A; --t2: #475569;  --t3: #94A3B8;
    --blue:    #2563EB; --blue-l: #EFF6FF;
    --green:   #059669; --green-l: #ECFDF5;
    --amber:   #D97706; --amber-l: #FFFBEB;
    --red:     #DC2626; --red-l: #FEF2F2;
    --sh:      0 1px 4px rgba(0,0,0,0.07);
    --sh-md:   0 4px 16px rgba(0,0,0,0.10);
}

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: var(--bg) !important; color: var(--t1) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1280px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: var(--t1) !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: var(--t2) !important; font-size:.78rem !important;
    font-weight:700 !important; text-transform:uppercase !important; letter-spacing:.06em !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background:var(--bg) !important; border:1px solid var(--border) !important;
    color:var(--t1) !important; border-radius:8px !important; font-size:.9rem !important;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--blue) !important; font-weight:800 !important; }
[data-testid="stSidebar"] .stButton > button {
    background:var(--blue) !important; color:#fff !important; border:none !important;
    border-radius:8px !important; font-weight:700 !important; width:100% !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background:var(--surface) !important; border:1.5px solid var(--border) !important;
    border-radius:8px !important; color:var(--t1) !important;
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:.92rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color:var(--blue) !important; box-shadow:0 0 0 3px rgba(37,99,235,0.1) !important;
}
.stTextInput label p, .stTextArea label p, .stSelectbox label p, .stSlider label p {
    color:var(--t2) !important; font-size:.78rem !important;
    font-weight:700 !important; text-transform:uppercase !important; letter-spacing:.06em !important;
}
.stSelectbox > div > div {
    background:var(--surface) !important; border:1.5px solid var(--border) !important;
    border-radius:8px !important; color:var(--t1) !important;
}

/* ── Buttons ── */
.stButton > button {
    background:var(--blue) !important; color:#fff !important; border:none !important;
    border-radius:10px !important; font-weight:700 !important; font-size:.95rem !important;
    padding:.7rem 1.5rem !important; box-shadow:0 2px 8px rgba(37,99,235,0.28) !important;
    transition:all .15s !important; font-family:'Plus Jakarta Sans',sans-serif !important;
}
.stButton > button:hover { background:#1D4ED8 !important; transform:translateY(-1px) !important; }
.stDownloadButton > button {
    background:var(--surface) !important; color:var(--blue) !important;
    border:1.5px solid var(--blue) !important; border-radius:8px !important; font-weight:600 !important;
}
.stDownloadButton > button:hover { background:var(--blue-l) !important; }

/* ── Tabs ── */
.stTabs [data-testid="stTabsBar"] {
    background:var(--surface) !important; border-bottom:2px solid var(--border) !important; gap:0 !important;
}
.stTabs [role="tab"] {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-weight:700 !important;
    font-size:.92rem !important; color:var(--t3) !important;
    padding:.7rem 1.4rem !important; border-bottom:3px solid transparent !important;
}
.stTabs [role="tab"][aria-selected="true"] {
    color:var(--blue) !important; border-bottom:3px solid var(--blue) !important; background:transparent !important;
}

/* ── Metrics ── */
[data-testid="stMetricLabel"] p { color:var(--t2) !important; font-size:.72rem !important; font-weight:700 !important; text-transform:uppercase !important; letter-spacing:.07em !important; }
[data-testid="stMetricValue"]   { color:var(--t1) !important; font-family:'JetBrains Mono',monospace !important; font-weight:700 !important; }

/* ── Alerts ── */
.stSuccess { background:var(--green-l) !important; border:1px solid #6EE7B7 !important; border-radius:10px !important; }
.stSuccess p { color:#065F46 !important; }
.stError { background:var(--red-l) !important; border:1px solid #FCA5A5 !important; border-radius:10px !important; }
.stError p { color:#991B1B !important; }
.stInfo { background:var(--blue-l) !important; border:1px solid #BFDBFE !important; border-radius:10px !important; }
.stInfo p { color:#1E40AF !important; }
.stWarning { background:var(--amber-l) !important; border:1px solid #FCD34D !important; border-radius:10px !important; }
.stWarning p { color:#92400E !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    border:1px solid var(--border) !important; border-radius:10px !important;
    background:var(--surface) !important; box-shadow:var(--sh) !important;
}
[data-testid="stExpander"] summary { font-weight:600 !important; color:var(--t1) !important; }

/* ══════════════════════════════════════════
   CUSTOM COMPONENTS
══════════════════════════════════════════ */

/* Hero */
.hero {
    background: linear-gradient(135deg,#0F172A 0%,#1E3A5F 50%,#1D4ED8 100%);
    border-radius:16px; padding:2rem; margin-bottom:1.5rem;
    text-align:center; border:1px solid #2563EB;
    box-shadow:0 8px 32px rgba(37,99,235,0.15);
}
.hero h1  { color:#fff; font-size:2rem; font-weight:800; margin:0 0 .3rem; letter-spacing:-.5px; }
.hero p   { color:#93C5FD; font-size:.9rem; margin:0; }
.hero-chips { display:flex; justify-content:center; flex-wrap:wrap; gap:.4rem; margin-top:.9rem; }
.hero-chip  { background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.2); color:#E0F2FE; padding:.22rem .8rem; border-radius:50px; font-size:.72rem; font-weight:600; }

/* KPI */
.kpi-row { display:grid; grid-template-columns:repeat(4,1fr); gap:.85rem; margin-bottom:1.3rem; }
.kpi-box { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:1rem; box-shadow:var(--sh); position:relative; overflow:hidden; transition:box-shadow .2s,transform .2s; }
.kpi-box:hover { box-shadow:var(--sh-md); transform:translateY(-1px); }
.kpi-box .bar { position:absolute; top:0; left:0; width:3px; height:100%; border-radius:12px 0 0 12px; }
.kpi-box .val { font-size:1.5rem; font-weight:800; font-family:'JetBrains Mono',monospace; color:var(--t1); padding-left:.5rem; line-height:1.1; }
.kpi-box .lbl { font-size:.66rem; color:var(--t3); text-transform:uppercase; letter-spacing:.08em; font-weight:700; margin:.25rem 0 0 .5rem; }
.kpi-box .sub { font-size:.75rem; color:var(--t2); padding-left:.5rem; }

/* Section + badge */
.section-h { font-size:.9rem; font-weight:800; color:var(--t1); margin:1.3rem 0 .65rem; }
.badge { background:var(--blue-l); color:var(--blue); font-size:.68rem; font-weight:700; padding:.18rem .55rem; border-radius:20px; }

/* Divider */
.divider { border:none; border-top:1px solid var(--border); margin:1.2rem 0; }

/* CRM header */
.crm-header { background:linear-gradient(135deg,#1E3A5F,#2563EB); border-radius:14px; padding:1.3rem 1.6rem; margin-bottom:1.3rem; display:flex; align-items:center; justify-content:space-between; }

/* Progress */
.prog-bg   { background:var(--border); border-radius:4px; height:5px; margin-top:.35rem; }
.prog-fill { height:5px; border-radius:4px; }

/* Email */
.email-box { background:var(--surface); border:1px solid var(--border); border-left:3px solid #2563EB; border-radius:10px; padding:1.1rem 1.3rem; font-size:.88rem; line-height:1.8; color:#1E293B; white-space:pre-wrap; box-shadow:var(--sh); }

/* Tier card */
.tier-card { border:1px solid var(--border); border-radius:8px; padding:.8rem; font-size:.82rem; height:100%; }

/* ══════════════════════════════════════════
   PROPOSAL VIEWER
══════════════════════════════════════════ */
.proposal-wrapper {
    background:#fff; border:1px solid #E2E8F0; border-radius:16px;
    box-shadow:0 4px 24px rgba(0,0,0,0.07); overflow:hidden;
}
.proposal-header {
    background:linear-gradient(135deg,#0F172A,#1E3A5F);
    padding:1.6rem 2rem;
}
.proposal-header h2 { color:#fff; font-size:1.25rem; font-weight:800; margin:0 0 .25rem; }
.proposal-header span { color:#93C5FD; font-size:.8rem; }
.proposal-body { padding:1.8rem 2rem; }

/* Section card inside proposal */
.p-section {
    background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px;
    padding:1.1rem 1.4rem; margin-bottom:1rem;
    border-left:3px solid #2563EB;
}
.p-section.green  { border-left-color:#059669; }
.p-section.amber  { border-left-color:#D97706; }
.p-section.purple { border-left-color:#7C3AED; }
.p-section.red    { border-left-color:#DC2626; }
.p-section h3 {
    font-size:.82rem; font-weight:800; text-transform:uppercase;
    letter-spacing:.06em; color:#64748B; margin:0 0 .6rem;
}
.p-section p { font-size:.92rem; line-height:1.75; color:#1E293B; margin:0; }

/* Pricing cards */
.pricing-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-bottom:1rem; }
.price-card {
    border-radius:14px; padding:1.3rem 1.2rem;
    border:1px solid #E2E8F0; position:relative; overflow:hidden;
    transition:transform .15s, box-shadow .15s;
}
.price-card:hover { transform:translateY(-3px); box-shadow:0 8px 24px rgba(0,0,0,0.12); }
.price-card.basic      { background:#EFF6FF; }
.price-card.pro        { background:linear-gradient(135deg,#0F172A,#1E40AF); color:#fff; border-color:#2563EB; }
.price-card.enterprise { background:#FFFBEB; }
.price-badge { position:absolute; top:-.6rem; right:1rem; background:#F59E0B; color:#fff; font-size:.62rem; font-weight:800; padding:.2rem .65rem; border-radius:20px; text-transform:uppercase; letter-spacing:.07em; }
.price-title { font-size:1rem; font-weight:800; margin:0 0 .5rem; }
.price-desc  { font-size:.82rem; line-height:1.65; opacity:.85; }
.price-card.pro .price-title,
.price-card.pro .price-desc { color:#fff; }
</style>
"""
