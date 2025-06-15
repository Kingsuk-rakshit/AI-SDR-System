# agents/human_handoff_agent.py

import json
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger
from utils.gmail_utils import send_email  # reuse from OutreachAgent

logger = get_logger("HumanHandoffAgent")

class HumanHandoffAgent:
    def __init__(self, lead_source_path="data/leads.json", handoff_log_path="data/logs/handoff_log.json"):
        self.lead_source_path = Path(lead_source_path)
        self.handoff_log_path = Path(handoff_log_path)
        self.leads = self._load_leads()
        self.handoff_log_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_leads(self):
        if self.lead_source_path.exists():
            try:
                with open(self.lead_source_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("Failed to decode leads.json.")
        return []

    def _load_handoff_log(self):
        if self.handoff_log_path.exists():
            try:
                with open(self.handoff_log_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("handoff_log.json is malformed. Starting fresh.")
        return []

    def _save_handoff_log(self, leads):
        for lead in leads:
            lead["handoff_reason"] = lead.get("status")
            lead["handoff_time"] = datetime.now().isoformat()
        with open(self.handoff_log_path, "w") as f:
            json.dump(leads, f, indent=2)

    def route_to_human(self):
        handoff_leads = []
        for lead in self.leads:
            if lead.get("qualified") and lead.get("status") in ["interested", "reply_received"]:
                handoff_leads.append(lead)
                logger.info(f"🤝 Handing off lead to human SDR: {lead['name']} at {lead['company']}")

        self._save_handoff_log(handoff_leads)
        return handoff_leads

    def notify_human(self):
        leads = self.route_to_human()
        if leads:
            subject = f"[Newton AI] {len(leads)} Leads Require SDR Follow-up"
            body = "🔔 The following leads need human SDR support:\n\n"
            body += "\n".join([f"- {l['name']} ({l['company']}) - {l.get('email')}" for l in leads])
            send_email("sdr-team@ravian.ai", subject, body)
            logger.info("[📧] Human handoff notification email sent.")
        else:
            logger.info("[✅] No leads require human intervention.")
