"""
demo.py  —  CLI demo (no Streamlit needed)
Tests the full RAG pipeline end-to-end.

Usage:
    python demo.py
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\n❌  Set GEMINI_API_KEY in your .env file first!")
        print("    Get free key: https://aistudio.google.com\n")
        return

    from proposal_generator import ProposalGenerator

    gen = ProposalGenerator(api_key=api_key)

    # ── Seed demo data ────────────────────────────────────────────────────────
    gen.seed_demo_data()

    # ── Example client ────────────────────────────────────────────────────────
    client_data = {
        "company_name":      "HealthAI Solutions",
        "industry":          "Healthcare",
        "problem_statement": (
            "Our patient onboarding process takes 45 minutes, 3x the industry average. "
            "Staff spends 4+ hours/day on manual paperwork instead of patient care. "
            "We lose 30% of potential patients before their first appointment due to slow follow-ups."
        ),
        "goals": (
            "Automate 70% of administrative workflows using AI. "
            "Reduce onboarding from 45 minutes to under 10 minutes. "
            "Expand from 2 to 5 clinic locations within 12 months."
        ),
        "budget_min":      200_000,
        "budget_max":      450_000,
        "timeline_months": 12,
        "team_size":       120,
        "current_revenue": 5_000_000,
    }

    # ── Generate ──────────────────────────────────────────────────────────────
    proposal = gen.generate(
        client_data = client_data,
        k           = 2,
        filters     = {"industry": "Healthcare"}
    )

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 58)
    print("  PROPOSAL SUMMARY")
    print("=" * 58)
    print(f"  ROI              : {proposal.get('roi_percentage')}%")
    print(f"  Total Investment : ${proposal.get('total_investment', 0):,}")
    total_rev = sum(proposal.get("monthly_revenue_projection", []))
    print(f"  12-Month Revenue : ${total_rev:,}")
    print(f"  Payback Period   : {proposal.get('payback_period_months')} months")
    print(f"  Math Check       : {proposal.get('_roi_math_check', 'N/A')}")

    print("\n  Executive Summary:")
    summary = proposal.get("executive_summary", "")
    print(f"  {summary[:300]}{'...' if len(summary) > 300 else ''}")

    print("\n  Budget Allocation:")
    for k, v in proposal.get("budget_allocation", {}).items():
        bar = "█" * (v // 5)
        print(f"    {k:12s}: {v:3d}%  {bar}")

    print("\n  Monthly Revenue ($):")
    rev = proposal.get("monthly_revenue_projection", [])
    for i, r in enumerate(rev, 1):
        bar = "▓" * (r // 10000)
        print(f"    M{i:02d}: ${r:>8,}  {bar}")

    print("\n  Phases:")
    for phase in proposal.get("proposed_solution", {}).get("phases", []):
        print(f"    {phase.get('phase')} — {phase.get('name')} ({phase.get('duration')})")

    print(f"\n  Output saved → output/ folder")
    print("=" * 58)


if __name__ == "__main__":
    main()
