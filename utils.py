"""
utils.py — CRM helpers for AI Sales Intelligence Platform
  - _build_crm_entry()   : proposal + client_data → CRM dict
  - _entries_to_csv()    : list of CRM entries → CSV bytes
  - _load_crm()          : JSON file → list
  - _save_crm()          : list → JSON file
"""

import io
import csv
import json
from datetime import datetime


def _build_crm_entry(proposal: dict, client_data: dict) -> dict:
    """Convert a generated proposal + client data into a CRM entry dict."""
    company  = client_data.get("company_name", "")
    industry = client_data.get("industry", "")
    budget   = f"${client_data.get('budget_min',0):,} – ${client_data.get('budget_max',0):,}"

    email_raw = proposal.get("_followup_email", "")
    subject   = next(
        (l.split(":", 1)[1].strip() for l in email_raw.split("\n")
         if l.lower().startswith("subject:")), ""
    )
    inv = proposal.get(
        "total_investment",
        int((client_data.get("budget_min", 0) + client_data.get("budget_max", 0)) / 2)
    )

    return {
        "lead_info": {
            "name":            company,
            "industry":        industry,
            "estimated_value": budget,
            "budget_num":      inv,
            "status":          "Proposal Sent",
            "added_at":        datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "proposal_metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "summary":      proposal.get("executive_summary", "")[:220] + "...",
            "roi":          proposal.get("roi_percentage", 0),
            "payback":      proposal.get("payback_period_months", "N/A"),
        },
        "follow_up_email": {
            "subject": subject,
            "body":    email_raw,
            "status":  "Draft — Not Sent",
        },
        "deal": {
            "stage":          "Proposal Sent",
            "probability":    55,
            "weighted_value": int(inv * 0.55),
            "next_action":    "Follow-up in 3 days",
        },
    }


def _entries_to_csv(entries: list) -> bytes:
    """Convert list of CRM entries to CSV bytes for download."""
    if not entries:
        return b""
    buf    = io.StringIO()
    fields = [
        "Name", "Industry", "Budget", "Est. Value", "Status", "Stage",
        "Probability", "Weighted Value", "ROI %", "Payback", "Email Subject",
        "Added At", "Summary",
    ]
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    for e in entries:
        li   = e.get("lead_info", {})
        deal = e.get("deal", {})
        meta = e.get("proposal_metadata", {})
        fu   = e.get("follow_up_email", {})
        w.writerow({
            "Name":           li.get("name", ""),
            "Industry":       li.get("industry", ""),
            "Budget":         li.get("estimated_value", ""),
            "Est. Value":     li.get("budget_num", 0),
            "Status":         li.get("status", ""),
            "Stage":          deal.get("stage", ""),
            "Probability":    deal.get("probability", ""),
            "Weighted Value": deal.get("weighted_value", ""),
            "ROI %":          meta.get("roi", ""),
            "Payback":        meta.get("payback", ""),
            "Email Subject":  fu.get("subject", "") if isinstance(fu, dict) else "",
            "Added At":       li.get("added_at", ""),
            "Summary":        meta.get("summary", ""),
        })
    return buf.getvalue().encode()


def _load_crm(path: str = "crm_data.json") -> list:
    """Load CRM entries from JSON file. Returns [] if file missing or corrupt."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_crm(entries: list, path: str = "crm_data.json") -> None:
    """Persist CRM entries to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
