# ⚡ AI Sales Intelligence Platform — RAG + Gemini

> Generate personalized sales proposals using FAISS vector search + Google Gemini 2.5 Flash

---

## 📁 Project Structure

```
rag_sales_platform/
│
├── .env                    ← 🔑 Your API keys go here (fill this first!)
├── requirements.txt        ← pip install -r requirements.txt
│
├── app.py                  ← 🖥️  Streamlit UI  (streamlit run app.py)
├── demo.py                 ← ⚡  CLI demo      (python demo.py)
│
├── proposal_generator.py   ← 🎯  Main pipeline orchestrator
├── rag_engine.py           ← 🔍  FAISS vector store
├── llm_client.py           ← 🤖  Gemini client + JSON extraction
│
├── data/                   ← Auto-created
│   ├── faiss.index         ← FAISS vector index
│   └── proposal_store.pkl  ← Metadata store
│
└── output/                 ← Auto-created — generated proposal JSONs saved here
```

---

## 🚀 Setup (5 Minutes)

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Get free Gemini API key
→ Go to **https://aistudio.google.com**
→ Sign in with Google
→ Click **"Get API Key"** → **"Create API key"**
→ Copy the key (starts with `AIzaSy...`)

### Step 3 — Fill in .env file
Open `.env` and replace `your_gemini_api_key_here`:
```
GEMINI_API_KEY=AIzaSy_your_actual_key_here
```

### Step 4 — Run!
```bash
# Option A: Streamlit UI (recommended)
streamlit run app.py

# Option B: CLI demo
python demo.py
```

---

## 🧠 How RAG Works

```
New Client Query
       │
       ▼
[1] Embed query → 384-dim vector (all-MiniLM-L6-v2, runs locally)
       │
       ▼
[2] FAISS similarity search → retrieve top-K past proposals
       │
       ▼
[3] Build prompt: system + retrieved context + client data
       │
       ▼
[4] Gemini 2.5 Flash generates personalized proposal JSON
       │
       ▼
[5] Validate: fix budget %, fix revenue array, recalculate ROI
       │
       ▼
[6] Store new proposal back in FAISS (platform learns over time!)
       │
       ▼
Final JSON → Streamlit UI + saved to output/
```

---

## 📊 Output JSON Structure

```json
{
  "executive_summary": "Personalized 3-4 sentence summary...",
  "problem_analysis": {
    "primary_challenges": ["challenge 1", "challenge 2", "challenge 3"],
    "revenue_impact": "$500,000/year"
  },
  "proposed_solution": {
    "overview": "Solution overview...",
    "phases": [
      {"phase": "Phase 1", "name": "Foundation",   "duration": "3 months", "key_deliverables": [...]},
      {"phase": "Phase 2", "name": "Acceleration", "duration": "5 months", "key_deliverables": [...]},
      {"phase": "Phase 3", "name": "Optimization", "duration": "4 months", "key_deliverables": [...]}
    ]
  },
  "budget_allocation": {"marketing": 35, "technology": 30, "operations": 20, "hr": 15},
  "monthly_revenue_projection": [28000, 38000, 52000, 71000, 90000, 108000, 122000, 138000, 152000, 163000, 180000, 195000],
  "total_investment": 480000,
  "roi_percentage": 179,
  "payback_period_months": 6,
  "why_us": ["point 1", "point 2", "point 3"],
  "next_steps": "Call to action...",
  "_roi_math_check": "(1,337,000 - 480,000) / 480,000 × 100 = 179%"
}
```

---

## 🏆 Hackathon Pitch Line

> *"We implemented Retrieval-Augmented Generation to personalize proposals using historical sales intelligence. Our FAISS vector store indexes past proposals as 384-dimensional embeddings. When a new client query arrives, we retrieve semantically similar proposals and inject them as context into Gemini 2.5 Flash — so every proposal is grounded in real outcomes, not generic templates. The platform continuously learns by storing each new proposal back into the vector store."*

---

## ⚙️ Advanced Usage

```python
from proposal_generator import ProposalGenerator

gen = ProposalGenerator()  # reads GEMINI_API_KEY from .env automatically

proposal = gen.generate(
    client_data = {
        "company_name":      "MyStartup",
        "industry":          "Healthcare",
        "problem_statement": "...",
        "goals":             "...",
        "budget_min":        100_000,
        "budget_max":        400_000,
        "timeline_months":   12,
        "team_size":         80,
        "current_revenue":   3_000_000,
    },
    k       = 3,                            # retrieve top-3 similar
    filters = {"industry": "Healthcare"},   # only same industry
    save    = True,                         # save JSON to output/
)
```
