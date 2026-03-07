"""
llm_client.py  —  Google Gemini Client with RAG Context Injection
Handles: Prompt building → Gemini API call → Error-safe JSON extraction
"""

import os
import re
import json
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARNING] Run: pip install google-genai")

# ── Config ────────────────────────────────────────────────────────────────────
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_TOKENS   = 8192
TEMPERATURE  = 1.0   # Gemini 2.5 requires temperature=1 for thinking models

SYSTEM_PROMPT = """You are an elite AI Sales Intelligence Assistant.
You generate highly personalized, data-driven sales proposals using past successful proposals as reference.

STRICT RULES:
- Be specific with numbers, percentages, and timelines
- Personalize every section to the client's exact industry and pain points
- Return ONLY valid JSON — no markdown fences, no extra text, no explanation
- Ensure budget_allocation percentages always sum to exactly 100
- Make monthly_revenue projections realistic and gradually increasing
- ROI must be mathematically correct: (sum_of_monthly_revenue - investment) / investment * 100"""


# ── Prompt Builder ────────────────────────────────────────────────────────────
def build_rag_prompt(client_data: dict, similar_proposals: list) -> str:
    """Builds RAG-augmented prompt by injecting retrieved context."""

    context_block = ""
    if similar_proposals:
        context_block = "\n\n## RETRIEVED SIMILAR PROPOSALS (Use as strategic reference)\n"
        for i, p in enumerate(similar_proposals[:2], 1):
            meta      = p["metadata"]
            score_pct = int(p["score"] * 100)
            context_block += f"""
--- Reference #{i} (Similarity Score: {score_pct}%) ---
Industry  : {meta.get('industry', 'N/A')}
Budget    : ${meta.get('budget', 0):,}
ROI       : {meta.get('roi', 'N/A')}%
Summary   : {p['text'][:600]}
"""
    else:
        context_block = "\n\n## No similar proposals found — generate from scratch based on client data.\n"

    prompt = f"""{context_block}

## NEW CLIENT DETAILS
Company        : {client_data.get('company_name', 'Client')}
Industry       : {client_data.get('industry', 'Technology')}
Problem        : {client_data.get('problem_statement', '')}
Goals          : {client_data.get('goals', '')}
Budget Range   : ${client_data.get('budget_min', 50000):,} – ${client_data.get('budget_max', 500000):,}
Timeline       : {client_data.get('timeline_months', 12)} months
Team Size      : {client_data.get('team_size', 50)} employees
Current Revenue: ${client_data.get('current_revenue', 0):,}/year

## TASK
Generate a complete, personalized sales proposal as a single JSON object with this exact structure:

{{
  "executive_summary": "3-4 sentences, specific to their industry and problems",
  "problem_analysis": {{
    "primary_challenges": ["challenge 1 with specific cost impact", "challenge 2 with metric", "challenge 3"],
    "revenue_impact": "Estimated annual revenue loss e.g. $500,000/year"
  }},
  "proposed_solution": {{
    "overview": "One paragraph solution summary",
    "phases": [
      {{
        "phase": "Phase 1",
        "name": "Foundation",
        "duration": "3 months",
        "key_deliverables": ["deliverable 1", "deliverable 2", "deliverable 3"]
      }},
      {{
        "phase": "Phase 2",
        "name": "Acceleration",
        "duration": "5 months",
        "key_deliverables": ["deliverable 1", "deliverable 2", "deliverable 3"]
      }},
      {{
        "phase": "Phase 3",
        "name": "Optimization",
        "duration": "4 months",
        "key_deliverables": ["deliverable 1", "deliverable 2", "deliverable 3"]
      }}
    ]
  }},
  "budget_allocation": {{
    "technology": 35,
    "operations": 25,
    "marketing": 25,
    "hr": 15
  }},
  "monthly_revenue_projection": [28000, 38000, 52000, 71000, 90000, 108000, 122000, 138000, 152000, 163000, 180000, 195000],
  "total_investment": 480000,
  "roi_percentage": 179,
  "payback_period_months": 6,
  "why_us": [
    "Point 1 specific to client industry with a concrete metric",
    "Point 2 about technical capability relevant to their problem",
    "Point 3 about risk reduction or guarantee"
  ],
  "next_steps": "Specific call to action with a concrete date or timeline"
}}

IMPORTANT: Customize ALL values to match the client's industry, budget range, and goals.
Return ONLY the JSON object. Nothing else."""

    return prompt


def build_email_prompt(client_data: dict, proposal: dict) -> str:
    """Builds follow-up email prompt using generated proposal data."""
    return f"""Write a short, professional follow-up sales email for this proposal.

Client      : {client_data.get('company_name')}
Industry    : {client_data.get('industry')}
Key Problem : {client_data.get('problem_statement', '')[:120]}
ROI         : {proposal.get('roi_percentage', 'N/A')}%
Investment  : ${proposal.get('total_investment', 0):,}
Payback     : {proposal.get('payback_period_months', 'N/A')} months

Rules:
- FIRST LINE must be exactly: Subject: [your subject line here]
- Under 160 words total
- Warm but professional tone
- Reference ONE specific number from the proposal (ROI or payback)
- Clear CTA: schedule a 30-min discovery call this week
- End with: Best regards, [Your Name]

Write ONLY the email. No explanation, no extra text."""


# ── GeminiClient ──────────────────────────────────────────────────────────────
class GeminiClient:
    """Google Gemini API wrapper with retry logic and error-safe JSON extraction."""

    def __init__(self, api_key: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("Install: pip install google-genai")

        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key or key == "your_gemini_api_key_here":
            raise ValueError(
                "Set GEMINI_API_KEY in your .env file!\n"
                "Get free key at: https://aistudio.google.com"
            )

        self.client = genai.Client(api_key=key)
        self.model  = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
        print(f"[LLM] Gemini client ready — model: {self.model}")

    # ── Generate ──────────────────────────────────────────────────────────────
    def generate(self, prompt: str, max_retries: int = 3,
                 use_system: bool = True) -> str:
        """Call Gemini API with exponential backoff on errors."""
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}" if use_system else prompt

        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model    = self.model,
                    contents = full_prompt,
                )
                text = response.text
                print(f"[LLM] Generated {len(text)} chars | attempt={attempt}")
                return text

            except Exception as e:
                err = str(e).lower()
                if "quota" in err or "429" in err or "rate" in err:
                    wait = 2 ** attempt
                    print(f"[LLM] Rate limit hit. Waiting {wait}s...")
                    time.sleep(wait)
                elif attempt == max_retries:
                    raise RuntimeError(f"Gemini API failed after {max_retries} attempts: {e}")
                else:
                    print(f"[LLM] Attempt {attempt} failed: {e}. Retrying in 2s...")
                    time.sleep(2)

        raise RuntimeError(f"Gemini API failed after {max_retries} attempts.")

    # ── JSON Extraction ───────────────────────────────────────────────────────
    @staticmethod
    def extract_json(raw: str) -> dict:
        """
        Robustly extract JSON from LLM output.
        Handles: markdown fences, leading text, trailing comments.
        """
        # 1. Strip markdown fences
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        raw = re.sub(r"```", "", raw).strip()

        # 2. Find first opening brace
        start = raw.find("{")
        if start == -1:
            raise ValueError(f"No JSON object found in response. Raw preview: {raw[:200]}")

        # 3. Find matching closing brace
        depth, end = 0, -1
        for i, ch in enumerate(raw[start:], start=start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        if end == -1:
            raise ValueError("Unclosed JSON object in LLM response.")

        json_str = raw[start:end]

        # 4. Fix common LLM JSON mistakes
        json_str = re.sub(r",\s*([}\]])", r"\1", json_str)        # trailing commas
        json_str = re.sub(r"//[^\n]*", "", json_str)               # JS comments
        json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.S)  # block comments

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"JSON parse failed: {e}\n"
                f"Problematic JSON (first 400 chars):\n{json_str[:400]}"
            )
