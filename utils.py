import json
import csv
import io
import re
from datetime import datetime
from fpdf import FPDF

# PDF

def create_pdf(proposal_text: str, client_name: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.add_font("Roboto", "", "Roboto-Regular.ttf")
        pdf.set_font("Roboto", size=16)
    except Exception:
        pdf.set_font("Helvetica", size=16)

    pdf.cell(200, 10, txt=f"Proposal for {client_name}", ln=True, align="C")
    pdf.ln(10)

    try:
        pdf.set_font("Roboto", size=11)
    except Exception:
        pdf.set_font("Helvetica", size=11)

    pdf.multi_cell(0, 10, txt=proposal_text)

    filename = f"Proposal_{client_name.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename


# CRM JSON

def create_crm_json(client_name: str, sector: str, budget: str, proposal_text: str) -> str:
    """Base CRM entry as JSON string (original function — kept intact)."""
    crm_data = {
        "lead_info": {
            "name":            client_name,
            "industry":        sector,
            "estimated_value": budget,
            "status":          "Proposal Sent",
        },
        "proposal_metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "summary":      proposal_text[:300] + ("..." if len(proposal_text) > 300 else ""),
            "file_type":    "PDF",
        },
    }
    return json.dumps(crm_data, indent=4, ensure_ascii=False)


def build_full_crm_entry(
    client_name: str,
    sector: str,
    budget: str,
    proposal_text: str,
    followup_email: str = "",
) -> dict:
    """
    Builds on create_crm_json() and adds:
    - follow_up_email (full body — not truncated)
    - pricing_tiers  (parsed from proposal)
    - deal stage / probability / weighted value
    - timestamps
    """
    base = json.loads(create_crm_json(client_name, sector, budget, proposal_text))

    # budget → number
    nums = re.findall(r"[\d,]+", str(budget).replace("k", "000").replace("K", "000"))
    budget_num = (
        int(sum(int(n.replace(",", "")) for n in nums) / max(len(nums), 1))
        if nums
        else 0
    )

    # pricing tiers 
    # pricing = {}
    # for tier in ["Basic", "Pro", "Enterprise"]:
    #     m = re.search(
    #         rf"(?:###?\s*{tier}[^\n]*\n)(.*?)(?=###|\Z)",
    #         proposal_text,
    #         re.DOTALL | re.IGNORECASE,
    #     )
    #     if m:
    #         pricing[tier] = m.group(1).strip()  # full text, no truncation

    # ── email subject ────────────────────────────────────────────────────────
    subject = ""
    for line in followup_email.split("\n"):
        if line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
            break

    base.update(
        {
            "lead_info": {
                **base["lead_info"],
                "budget_num": budget_num,
                "added_at":   datetime.now().strftime("%Y-%m-%d %H:%M"),
            },
            "proposal_metadata": {
                **base["proposal_metadata"],
                # "full_proposal": proposal_text,          # full text saved
            },
            # "follow_up_email": {
            #     "subject": subject,
            #     "body":    followup_email,               # full email saved
            #     "status":  "Draft — Not Sent",
            # },
            # "pricing_tiers": pricing,
            "deal": {
                "stage":          "Proposal Sent",
                "probability":    55,
                "weighted_value": int(budget_num * 0.55),
                "next_action":    "Follow-up in 3 days",
            },
        }
    )
    return base

# CSV export

def entries_to_csv(entries: list) -> bytes:
    if not entries:
        return b""
    buf = io.StringIO()
    fields = [
        "Name", "Industry", "Budget", "Est. Value",
        "Status", "Stage", "Probability", "Weighted Value",
        "Email Subject", "Added At", "Summary",
    ]
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    for e in entries:
        li   = e.get("lead_info", {})
        deal = e.get("deal", {})
        meta = e.get("proposal_metadata", {})
        fu   = e.get("follow_up_email", {})
        w.writerow(
            {
                "Name":           li.get("name", ""),
                "Industry":       li.get("industry", ""),
                "Budget":         li.get("estimated_value", ""),
                "Est. Value":     li.get("budget_num", 0),
                "Status":         li.get("status", ""),
                "Stage":          deal.get("stage", ""),
                "Probability":    deal.get("probability", ""),
                "Weighted Value": deal.get("weighted_value", ""),
                "Email Subject":  fu.get("subject", "") if isinstance(fu, dict) else "",
                "Added At":       li.get("added_at", ""),
                "Summary":        meta.get("summary", ""),
            }
        )
    return buf.getvalue().encode()

# Persistent CRM (file-backed, survives Streamlit reruns within same session)

CRM_FILE = "crm_data.json"


def load_crm() -> list:
    """Load CRM entries from disk. Returns [] on first run or errors."""
    try:
        with open(CRM_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_crm(entries: list) -> None:
    """Persist CRM entries to disk."""
    with open(CRM_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
