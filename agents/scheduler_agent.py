# agents/scheduler_agent.py

import json
from utils.logger import get_logger
from config import CALENDLY_LINK
from pathlib import Path

logger = get_logger("SchedulerAgent")

class SchedulerAgent:
    def __init__(self, lead_source_path="data/leads.json"):
        self.lead_source_path = Path(lead_source_path)
        self.leads = self._load_leads()

    def _load_leads(self):
        if self.lead_source_path.exists():
            with open(self.lead_source_path, "r") as f:
                return json.load(f)
        logger.warning("⚠️ Leads file not found.")
        return []

    def _save_leads(self):
        with open(self.lead_source_path, "w") as f:
            json.dump(self.leads, f, indent=2)

    def schedule_meetings(self):
        meetings_scheduled = []
        for lead in self.leads:
            if (
                lead.get("qualified")
                and lead.get("status") in ["interested", "book_meeting"]
                and not lead.get("meeting_scheduled")
            ):
                calendly_url = f"{CALENDLY_LINK}?name={lead['name'].replace(' ', '%20')}&email={lead['email']}"
                lead["meeting_scheduled"] = calendly_url

                meetings_scheduled.append({
                    "name": lead["name"],
                    "email": lead["email"],
                    "company": lead.get("company", ""),
                    "calendly_link": calendly_url
                })

                logger.info(f"📅 Scheduled Calendly meeting for {lead['name']} → {calendly_url}")

        self._save_leads()
        return meetings_scheduled
