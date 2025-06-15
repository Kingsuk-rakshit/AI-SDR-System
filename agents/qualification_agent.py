# agents/qualification_agent.py

import json
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("QualificationAgent")

# ✅ Ideal Customer Profile - tweak this as needed
DEFAULT_ICP = {
    "target_roles": ["CTO", "VP of Engineering", "Head of ML", "Director of AI", "AI Lead"],
    "target_domains": ["ai", "ml", "data", "tech", "analytics"],
    "min_score": 2  # out of 3
}

class QualificationAgent:
    def __init__(self, lead_source_path="data/leads.json", icp_criteria=None):
        self.lead_source_path = Path(lead_source_path)
        self.icp = icp_criteria or DEFAULT_ICP
        self.leads = self._load_leads()

    def _load_leads(self):
        if self.lead_source_path.exists():
            try:
                with open(self.lead_source_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("⚠️ Invalid leads JSON format.")
                return []
        else:
            logger.warning("⚠️ No leads file found at path.")
            return []

    def _save_leads(self):
        with open(self.lead_source_path, "w", encoding="utf-8") as f:
            json.dump(self.leads, f, indent=2, ensure_ascii=False)
        logger.info("💾 Leads updated and saved.")

    def _score_lead(self, lead):
        score = 0

        role = lead.get("role", "").lower()
        domain = lead.get("domain", "").lower()
        company = lead.get("company", "").lower()

        # Rule 1: Title match
        if any(role_keyword.lower() in role for role_keyword in self.icp["target_roles"]):
            score += 1

        # Rule 2: Domain match
        if any(keyword in domain for keyword in self.icp["target_domains"]):
            score += 1

        # Rule 3: Company keyword match (optional)
        if any(keyword in company for keyword in self.icp["target_domains"]):
            score += 1

        return score

    def qualify_leads(self):
        qualified = []
        for lead in self.leads:
            score = self._score_lead(lead)
            lead["score"] = score
            lead["qualified"] = score >= self.icp["min_score"]
            logger.info(f"🎯 Lead: {lead['name']} | Score: {score} | Qualified: {lead['qualified']}")
            qualified.append(lead)
        
        self.leads = qualified
        self._save_leads()

    def score_leads(self):
        self.qualify_leads()

    def get_qualified_leads(self):
        return [lead for lead in self.leads if lead.get("qualified")]

    def get_disqualified_leads(self):
        return [lead for lead in self.leads if not lead.get("qualified")]
