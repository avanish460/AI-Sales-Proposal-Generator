"""
proposal_generator.py  —  Main Pipeline Orchestrator
Flow: Client Data → RAG Search → Gemini Generation → Validate → Store → Return
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from rag_engine import RAGEngine
from llm_client import GeminiClient, build_rag_prompt


class ProposalGenerator:
    """
    AI Sales Intelligence Pipeline (Gemini + FAISS RAG):

    1. Receive client data
    2. FAISS search for similar past proposals
    3. Inject context into Gemini prompt
    4. Generate personalized proposal JSON
    5. Validate & auto-fix math errors
    6. Store back into FAISS (continuous learning!)
    7. Save output JSON to disk
    """

    def __init__(self, api_key: str = None):
        print("=" * 58)
        print("  ⚡ AI Sales Intelligence Platform  |  RAG + Gemini")
        print("=" * 58)
        self.rag        = RAGEngine()
        self.llm        = GeminiClient(api_key=api_key)
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
        self.output_dir.mkdir(exist_ok=True)

    # ── Main Pipeline ─────────────────────────────────────────────────────────
    def generate(self, client_data: dict, k: int = None,
                 filters: dict = None, save: bool = True) -> dict:
        """
        Full RAG pipeline. Returns structured proposal dict.

        Args:
            client_data : Dict with company info (see demo.py for example)
            k           : Number of similar proposals to retrieve (default: RAG_TOP_K from .env)
            filters     : Optional FAISS filters e.g. {"industry": "Healthcare"}
            save        : Whether to save output JSON to disk
        """
        k        = k or int(os.getenv("RAG_TOP_K", 3))
        company  = client_data.get("company_name", "Client")
        industry = client_data.get("industry", "")

        print(f"\n[PIPELINE] Client: {company} | Industry: {industry}")
        print("-" * 58)

        # ── Step 1: RAG Retrieval ─────────────────────────────────────────────
        print("[1/5] Searching FAISS vector store...")
        search_query = f"{industry} {client_data.get('goals', '')} {client_data.get('problem_statement', '')}"

        # Auto-apply industry filter if not overridden
        if filters is None and industry:
            filters = {"industry": industry}

        similar = self.rag.search(query=search_query, k=k, filters=filters)

        # If industry filter returns 0, retry without filter
        if not similar and filters:
            print("[1/5] No industry match — retrying without filters...")
            similar = self.rag.search(query=search_query, k=k, filters=None)

        print(f"[1/5] Retrieved {len(similar)} similar proposals.")
        for r in similar:
            print(f"      ↳ #{r['rank']} | score={r['score']} | {r['metadata'].get('company', 'N/A')}")

        # ── Step 2: Build Prompt ──────────────────────────────────────────────
        print("[2/5] Building RAG-augmented prompt...")
        prompt = build_rag_prompt(client_data, similar)

        # ── Step 3: Generate with Gemini ──────────────────────────────────────
        print("[3/5] Calling Gemini API...")
        raw_response = self.llm.generate(prompt)

        # ── Step 4: Parse JSON ────────────────────────────────────────────────
        print("[4/5] Parsing and validating JSON...")
        proposal = self.llm.extract_json(raw_response)
        proposal = self._validate_and_fix(proposal, client_data)

        # ── Step 5: Store in RAG (continuous learning) ────────────────────────
        print("[5/5] Storing proposal in FAISS for future retrieval...")
        summary = (
            f"Company: {company}. Industry: {industry}. "
            f"Summary: {proposal.get('executive_summary', '')[:300]}. "
            f"ROI: {proposal.get('roi_percentage', 0)}%. "
            f"Investment: ${proposal.get('total_investment', 0):,}."
        )
        self.rag.add_proposal(
            text     = summary,
            metadata = {
                "company":  company,
                "industry": industry,
                "budget":   proposal.get("total_investment", 0),
                "roi":      proposal.get("roi_percentage", 0),
                "date":     datetime.now().isoformat(),
            }
        )

        # ── Save to disk ──────────────────────────────────────────────────────
        if save:
            safe_name = company.replace(" ", "_").replace("/", "-")
            fname     = self.output_dir / f"{safe_name}_{datetime.now():%Y%m%d_%H%M%S}.json"
            with open(fname, "w", encoding="utf-8") as f:
                json.dump({
                    "generated_at":           datetime.now().isoformat(),
                    "client_data":            client_data,
                    "rag_context_used":       len(similar),
                    "proposal":               proposal,
                }, f, indent=2)
            print(f"\n[PIPELINE] Saved → {fname}")

        # ── Summary ───────────────────────────────────────────────────────────
        roi = proposal.get("roi_percentage", "N/A")
        inv = proposal.get("total_investment", 0)
        print(f"\n[PIPELINE] ✅ Done! ROI={roi}% | Investment=${inv:,}")
        return proposal

    # ── Validate & Fix ────────────────────────────────────────────────────────
    def _validate_and_fix(self, proposal: dict, client_data: dict) -> dict:
        """Auto-fix common LLM math errors in the proposal."""

        # 1. Budget allocation must sum to 100
        ba = proposal.get("budget_allocation", {})
        if ba:
            total = sum(ba.values())
            if total != 100:
                scale = 100 / total
                proposal["budget_allocation"] = {k: round(v * scale) for k, v in ba.items()}
                diff = 100 - sum(proposal["budget_allocation"].values())
                first_key = next(iter(proposal["budget_allocation"]))
                proposal["budget_allocation"][first_key] += diff

        # 2. Revenue projection must be exactly 12 months
        rev = proposal.get("monthly_revenue_projection", [])
        if len(rev) < 12:
            if rev:
                step = (rev[-1] - rev[0]) / max(len(rev) - 1, 1) if len(rev) > 1 else rev[0] * 0.1
                while len(rev) < 12:
                    rev.append(int(rev[-1] + step))
            else:
                # Generate fallback projection from budget
                budget = client_data.get("budget_max", 480000)
                rev    = [int(budget * r) for r in [0.06, 0.08, 0.11, 0.15, 0.19, 0.23,
                                                     0.25, 0.29, 0.32, 0.34, 0.38, 0.41]]
            proposal["monthly_revenue_projection"] = rev[:12]

        # 3. Recalculate ROI from actual numbers (always override LLM's value)
        total_rev  = sum(proposal["monthly_revenue_projection"])
        investment = proposal.get("total_investment", 0)
        if investment <= 0:
            investment = client_data.get("budget_max", 480000)
            proposal["total_investment"] = investment

        if investment > 0:
            proposal["roi_percentage"]  = round((total_rev - investment) / investment * 100)
            proposal["_roi_math_check"] = (
                f"({total_rev:,} - {investment:,}) / {investment:,} × 100 "
                f"= {proposal['roi_percentage']}%"
            )

        # 4. Recalculate payback period
        cumulative = 0
        for i, m in enumerate(proposal["monthly_revenue_projection"], 1):
            cumulative += m
            if cumulative >= investment:
                proposal["payback_period_months"] = i
                break

        return proposal

    # ── Seed Demo Data ────────────────────────────────────────────────────────
    def seed_demo_data(self):
        """Seeds FAISS with 5 sample proposals for demo. Skips if already seeded."""
        if self.rag.stats()["total_proposals"] > 0:
            print("[SEED] Index already has data. Skipping seed.")
            return

        samples = [
            {
                "text": (
                    "HealthAI — Healthcare NLP startup automated clinical documentation, "
                    "reducing admin burden by 60%. EHR integration + model training + deployment. "
                    "$320K investment, 165% ROI in 12 months. Staff hours freed: 1,400/month."
                ),
                "meta": {"company": "HealthAI",  "industry": "Healthcare",  "budget": 320000, "roi": 165}
            },
            {
                "text": (
                    "FinScale — Fintech SaaS implemented demand gen, ABM, and sales automation. "
                    "MRR grew from $80K to $240K. $240K budget, 210% ROI in 10 months. "
                    "CAC reduced by 45%, LTV:CAC ratio improved to 5:1."
                ),
                "meta": {"company": "FinScale",  "industry": "Fintech",     "budget": 240000, "roi": 210}
            },
            {
                "text": (
                    "ShopNova — E-commerce brand scaled from $2M to $8M ARR via omnichannel "
                    "marketing, Shopify Plus migration, and supply chain automation. "
                    "$180K investment, 190% ROI, 12 months."
                ),
                "meta": {"company": "ShopNova",  "industry": "E-commerce",  "budget": 180000, "roi": 190}
            },
            {
                "text": (
                    "LearnForge — EdTech startup launched enterprise LMS platform. "
                    "Custom content, sales hiring, ABM strategy. "
                    "$150K investment, 175% ROI, 45 enterprise clients in 12 months."
                ),
                "meta": {"company": "LearnForge","industry": "EdTech",      "budget": 150000, "roi": 175}
            },
            {
                "text": (
                    "FleetIQ — Logistics company deployed IoT + ML predictive maintenance. "
                    "Fleet downtime reduced 35%, fuel costs cut 22%. "
                    "$400K tech transformation, 155% ROI over 14 months."
                ),
                "meta": {"company": "FleetIQ",   "industry": "Logistics",   "budget": 400000, "roi": 155}
            },
        ]

        print(f"[SEED] Seeding {len(samples)} demo proposals into FAISS...")
        for s in samples:
            self.rag.add_proposal(s["text"], s["meta"])
        print(f"[SEED] ✅ Done — {len(samples)} proposals indexed.")
