# agents/prospector_agent.py

import json
from utils.enrichment_utils import enrich_lead
from utils.logger import get_logger
from pathlib import Path
from datetime import datetime

logger = get_logger("ProspectorAgent")

class ProspectorAgent:
    def __init__(self, lead_source_path="data/leads.json"):
        self.lead_source_path = Path(lead_source_path)
        self.leads = self._load_leads()

    def _load_leads(self):
        if self.lead_source_path.exists():
            try:
                with open(self.lead_source_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("Failed to decode existing leads JSON.")
                return []
        else:
            logger.info("No existing leads file found. Starting fresh.")
            return []

    def _save_leads(self):
        self.lead_source_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.lead_source_path, "w") as f:
            json.dump(self.leads, f, indent=2)

    def _is_duplicate(self, email):
        return any(lead.get("email") == email for lead in self.leads if email)

    def add_new_leads(self, raw_leads):
        new_entries = 0
        for lead in raw_leads:
            enriched = enrich_lead(lead)
            email = enriched.get("email")

            if email and not self._is_duplicate(email):
                enriched["status"] = "new"
                enriched["qualified"] = False
                enriched["score"] = 0
                enriched["sales_stage"] = "awareness"
                enriched["created_at"] = datetime.now().isoformat()

                self.leads.append(enriched)
                logger.info(f"✅ Added enriched lead: {enriched['name']} at {enriched['company']}")
                new_entries += 1
            else:
                logger.warning(f"⚠️ Duplicate or missing email for lead: {lead}")

        self._save_leads()
        logger.info(f"📈 Total new leads added: {new_entries}")

    def get_all_leads(self):
        return self.leads

    def get_new_leads(self):
        return [lead for lead in self.leads if lead.get("status") == "new"]
