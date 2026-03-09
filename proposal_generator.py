"""
proposal_generator.py  —  Main Pipeline Orchestrator
Flow: Client Data → RAG Search → Gemini Generation → Validate → Store → Return

Improvements over v1:
- RAG sources exposed in proposal (_rag_sources) — UI can show proof
- Full proposal text stored in FAISS (not just summary) — better future retrieval
- Follow-up email generated as second Gemini call (_followup_email)
- Specific JSON parse error retry with stricter prompt
- Seed data expanded to 8 proposals (more industries covered)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from rag_engine import RAGEngine
from llm_client import GeminiClient, build_rag_prompt, build_email_prompt


class ProposalGenerator:
    """
    AI Sales Intelligence Pipeline (Gemini + FAISS RAG):

    1. Receive client data
    2. FAISS search for similar past proposals
    3. Inject retrieved context into Gemini prompt
    4. Generate personalized proposal JSON
    5. Validate & auto-fix all math errors
    6. Generate follow-up email (second Gemini call)
    7. Store full proposal back into FAISS (continuous learning)
    8. Save output JSON to disk
    """

    def __init__(self, api_key: str = None):
        print("=" * 60)
        print("  ⚡ AI Sales Intelligence Platform  |  RAG + Gemini v2")
        print("=" * 60)
        self.rag        = RAGEngine()
        self.llm        = GeminiClient(api_key=api_key)
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
        self.output_dir.mkdir(exist_ok=True)

    # ── Main Pipeline ─────────────────────────────────────────────────────────
    def generate(self, client_data: dict, k: int = None,
                 filters: dict = None, save: bool = True) -> dict:
        """
        Full RAG + Generation pipeline. Returns structured proposal dict.

        Args:
            client_data : Dict with company info
            k           : Number of similar proposals to retrieve
            filters     : Optional FAISS filters e.g. {"industry": "Healthcare"}
            save        : Whether to save output JSON to disk
        """
        k        = k or int(os.getenv("RAG_TOP_K", 3))
        company  = client_data.get("company_name", "Client")
        industry = client_data.get("industry", "")

        print(f"\n[PIPELINE] Client: {company} | Industry: {industry}")
        print("-" * 60)

        # ── Step 1: RAG Retrieval ─────────────────────────────────────────────
        print("[1/6] Searching FAISS vector store...")
        search_query = (
            f"{industry} "
            f"{client_data.get('goals', '')} "
            f"{client_data.get('problem_statement', '')}"
        )

        if filters is None and industry:
            filters = {"industry": industry}

        similar = self.rag.search(query=search_query, k=k, filters=filters)

        # Fallback — retry without industry filter
        if not similar and filters:
            print("[1/6] No industry match — retrying without filters...")
            similar = self.rag.search(query=search_query, k=k, filters=None)

        print(f"[1/6] Retrieved {len(similar)} similar proposals.")
        for r in similar:
            print(f"      ↳ #{r['rank']} | score={r['score']:.3f} | "
                  f"{r['metadata'].get('company', 'N/A')} "
                  f"({r['metadata'].get('industry', 'N/A')})")

        # ── Step 2: Build Prompt ──────────────────────────────────────────────
        print("[2/6] Building RAG-augmented prompt...")
        prompt = build_rag_prompt(client_data, similar)

        # ── Step 3: Generate Proposal JSON ───────────────────────────────────
        print("[3/6] Calling Gemini API for proposal...")
        raw_response = self.llm.generate(prompt)

        # ── Step 4: Parse + Validate ──────────────────────────────────────────
        print("[4/6] Parsing and validating JSON...")
        try:
            proposal = self.llm.extract_json(raw_response)
        except ValueError as json_err:
            # Retry with stricter prompt
            print(f"[4/6] JSON parse failed — retrying with stricter prompt...")
            retry_prompt = (
                prompt +
                "\n\nCRITICAL REMINDER: Your response must be ONLY a valid JSON object. "
                "No text before it. No text after it. No markdown. Start with {{ and end with }}."
            )
            raw_response = self.llm.generate(retry_prompt)
            proposal     = self.llm.extract_json(raw_response)

        proposal = self._validate_and_fix(proposal, client_data)

        # ── Step 5: Generate Follow-up Email ─────────────────────────────────
        print("[5/6] Generating follow-up email...")
        try:
            email_prompt  = build_email_prompt(client_data, proposal)
            email_raw     = self.llm.generate(email_prompt, use_system=False)
            proposal["_followup_email"] = email_raw.strip()
        except Exception as e:
            print(f"[5/6] Email generation failed (non-critical): {e}")
            proposal["_followup_email"] = ""

        # ── Attach RAG sources for UI display ─────────────────────────────────
        proposal["_rag_sources"] = [
            {
                "company":  r["metadata"].get("company",  "N/A"),
                "industry": r["metadata"].get("industry", "N/A"),
                "roi":      r["metadata"].get("roi",      "N/A"),
                "budget":   r["metadata"].get("budget",   0),
                "score":    r["score"],
                "summary":  r["text"][:180],
            }
            for r in similar
        ]
        proposal["_rag_count"] = len(similar)

        # ── Step 6: Store Full Proposal in FAISS (Continuous Learning) ────────
        print("[6/6] Storing proposal in FAISS for future retrieval...")
        store_text = (
            f"Company: {company}. Industry: {industry}. "
            f"Problem: {client_data.get('problem_statement', '')[:200]}. "
            f"Goals: {client_data.get('goals', '')[:150]}. "
            f"Summary: {proposal.get('executive_summary', '')[:300]}. "
            f"ROI: {proposal.get('roi_percentage', 0)}%. "
            f"Investment: ${proposal.get('total_investment', 0):,}. "
            f"Payback: {proposal.get('payback_period_months', 'N/A')} months."
        )
        self.rag.add_proposal(
            text     = store_text,
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
            # Don't save internal _ keys to disk
            clean_proposal = {k: v for k, v in proposal.items()
                              if not k.startswith("_")}
            with open(fname, "w", encoding="utf-8") as f:
                json.dump({
                    "generated_at":     datetime.now().isoformat(),
                    "client_data":      client_data,
                    "rag_context_used": len(similar),
                    "proposal":         clean_proposal,
                }, f, indent=2, ensure_ascii=False)
            print(f"\n[PIPELINE] Saved → {fname}")

        roi = proposal.get("roi_percentage", "N/A")
        inv = proposal.get("total_investment", 0)
        print(f"\n[PIPELINE] ✅ Done! ROI={roi}% | Investment=${inv:,} | "
              f"RAG sources={len(similar)}")
        return proposal

    # ── Validate & Fix ────────────────────────────────────────────────────────
    def _validate_and_fix(self, proposal: dict, client_data: dict) -> dict:
        """Auto-fix common LLM math errors in the proposal."""

        # 1. Budget allocation must sum to exactly 100
        ba = proposal.get("budget_allocation", {})
        if ba:
            total = sum(ba.values())
            if total != 100:
                scale = 100 / total
                proposal["budget_allocation"] = {
                    k: round(v * scale) for k, v in ba.items()
                }
                # Fix rounding drift
                diff      = 100 - sum(proposal["budget_allocation"].values())
                first_key = next(iter(proposal["budget_allocation"]))
                proposal["budget_allocation"][first_key] += diff

        # 2. Revenue projection must be exactly 12 months
        rev = proposal.get("monthly_revenue_projection", [])
        if len(rev) < 12:
            if rev:
                step = (
                    (rev[-1] - rev[0]) / max(len(rev) - 1, 1)
                    if len(rev) > 1
                    else rev[0] * 0.1
                )
                while len(rev) < 12:
                    rev.append(int(rev[-1] + step))
            else:
                budget = client_data.get("budget_max", 480000)
                rev    = [int(budget * r) for r in
                          [0.06, 0.08, 0.11, 0.15, 0.19, 0.23,
                           0.25, 0.29, 0.32, 0.34, 0.38, 0.41]]
            proposal["monthly_revenue_projection"] = rev[:12]

        # 3. Ensure total_investment is within budget range
        budget_min = client_data.get("budget_min", 0)
        budget_max = client_data.get("budget_max", 999_999_999)
        investment = proposal.get("total_investment", 0)
        if investment <= 0 or investment > budget_max * 1.15:
            investment = int((budget_min + budget_max) / 2)
            proposal["total_investment"] = investment

        # 4. Recalculate ROI from actual numbers (always override LLM value)
        total_rev = sum(proposal["monthly_revenue_projection"])
        if investment > 0:
            proposal["roi_percentage"]  = round(
                (total_rev - investment) / investment * 100
            )
            proposal["_roi_math_check"] = (
                f"({total_rev:,} - {investment:,}) / {investment:,} × 100 "
                f"= {proposal['roi_percentage']}%"
            )

        # 5. Recalculate payback period from actual monthly data
        cumulative = 0
        for i, m in enumerate(proposal["monthly_revenue_projection"], 1):
            cumulative += m
            if cumulative >= investment:
                proposal["payback_period_months"] = i
                break
        else:
            proposal["payback_period_months"] = 12  # fallback

        return proposal

    # ── Seed Demo Data ────────────────────────────────────────────────────────
    def seed_demo_data(self):
        """Seeds FAISS with 8 sample proposals covering all major industries."""
        if self.rag.stats()["total_proposals"] > 0:
            print("[SEED] Index already has data. Skipping seed.")
            return

        samples = [
            # Healthcare
            {
                "text": (
                    "MediCare Plus — Healthcare clinic automated patient onboarding and clinical notes. "
                    "AI intake forms reduced onboarding from 45 mins to 10 mins. "
                    "No-show rate dropped from 34% to 7% via automated reminders. "
                    "$320K investment, 165% ROI in 12 months. Staff hours freed: 1,400/month."
                ),
                "meta": {"company": "MediCare Plus",  "industry": "Healthcare",     "budget": 320000, "roi": 165}
            },
            # Fintech
            {
                "text": (
                    "FinScale Capital — Fintech SaaS implemented AI KYC verification and automated reports. "
                    "KYC verification reduced from 7 days to 2 hours. MRR grew $80K to $240K. "
                    "$240K budget, 210% ROI in 10 months. CAC reduced by 45%, LTV:CAC ratio 5:1."
                ),
                "meta": {"company": "FinScale",       "industry": "Fintech",        "budget": 240000, "roi": 210}
            },
            # E-commerce
            {
                "text": (
                    "ShopNova — E-commerce brand scaled $2M to $8M ARR via omnichannel marketing "
                    "and supply chain automation. Shopify Plus migration improved conversion by 28%. "
                    "$180K investment, 190% ROI, 12 months. Cart abandonment reduced 40%."
                ),
                "meta": {"company": "ShopNova",       "industry": "E-commerce",     "budget": 180000, "roi": 190}
            },
            # EdTech
            {
                "text": (
                    "LearnForge — EdTech startup launched AI-powered LMS with adaptive learning paths. "
                    "Course completion rate improved from 19% to 64%. "
                    "$150K investment, 175% ROI, 45 enterprise clients in 12 months. "
                    "Instructor feedback time cut from 5 days to 6 hours."
                ),
                "meta": {"company": "LearnForge",     "industry": "EdTech",         "budget": 150000, "roi": 175}
            },
            # Logistics
            {
                "text": (
                    "FleetIQ — Logistics company deployed IoT and ML predictive maintenance. "
                    "Fleet downtime reduced 35%, fuel costs cut 22% via route optimization. "
                    "Real-time customer ETAs reduced inbound calls by 60%. "
                    "$400K tech transformation, 155% ROI over 14 months."
                ),
                "meta": {"company": "FleetIQ",        "industry": "Logistics",      "budget": 400000, "roi": 155}
            },
            # Manufacturing
            {
                "text": (
                    "PrecisionTech — Manufacturing plant deployed AI visual inspection and predictive maintenance. "
                    "Machine downtime reduced by 48 hours early warning system. "
                    "Defect miss rate dropped from 12% to 1.8%. Energy consumption down 24%. "
                    "$450K investment, 148% ROI in 18 months."
                ),
                "meta": {"company": "PrecisionTech",  "industry": "Manufacturing",  "budget": 450000, "roi": 148}
            },
            # Real Estate
            {
                "text": (
                    "NestFinder Realty — Real estate agency deployed AI property matching and lead follow-up. "
                    "Lead response time reduced from 3 days to 45 minutes. "
                    "Property listing descriptions generated in 2 minutes vs 4 hours manually. "
                    "$120K investment, 182% ROI in 10 months. Conversion rate up 38%."
                ),
                "meta": {"company": "NestFinder",     "industry": "Real Estate",    "budget": 120000, "roi": 182}
            },
            # SaaS
            {
                "text": (
                    "DevFlow SaaS — Software company implemented AI code assistant and automated documentation. "
                    "Engineering sprint boilerplate time reduced by 35%. "
                    "New developer onboarding cut from 6 weeks to 10 days. "
                    "$200K investment, 195% ROI in 12 months. Bug triage time down 70%."
                ),
                "meta": {"company": "DevFlow",        "industry": "SaaS",           "budget": 200000, "roi": 195}
            },
        ]

        print(f"[SEED] Seeding {len(samples)} demo proposals into FAISS...")
        for s in samples:
            self.rag.add_proposal(s["text"], s["meta"])
        print(f"[SEED] ✅ Done — {len(samples)} proposals indexed.")
