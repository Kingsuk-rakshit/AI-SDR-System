# agents/outreach_agent.py

import json
import os
import openai  # ✅ Replace AzureOpenAI import
from config import OPENAI_CONFIG
from utils.gmail_utils import send_email
from utils.logger import get_logger
from prompts import cold_email_prompt_template

logger = get_logger("OutreachAgent")

# ✅ Set global config (for openai>=1.x style API)
openai.api_key = OPENAI_CONFIG["api_key"]
openai.base_url = OPENAI_CONFIG["base_url"]
openai.api_type = OPENAI_CONFIG["api_type"]
openai.api_version = OPENAI_CONFIG["api_version"]

class OutreachAgent:
    def __init__(self, leads_file="data/leads.json"):
        self.leads_file = leads_file
        self.leads = self._load_leads()

    def _load_leads(self):
        if not os.path.exists(self.leads_file):
            logger.warning(f"{self.leads_file} not found. Returning empty lead list.")
            return []
        with open(self.leads_file, "r") as f:
            return json.load(f)

    def _save_leads(self):
        with open(self.leads_file, "w") as f:
            json.dump(self.leads, f, indent=2)
        logger.info("💾 Leads updated and saved.")

    def _generate_email_llm(self, lead):
        prompt = cold_email_prompt_template.replace("{{name}}", lead.get("name", "there"))
        prompt = prompt.replace("{{company}}", lead.get("company", "your company"))
        prompt = prompt.replace("{{domain}}", lead.get("domain", "yourdomain.com"))
        prompt = prompt.replace("{{role}}", lead.get("role", "professional"))

        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_CONFIG["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            logger.debug(f"📨 LLM Email Response:\n{content}")

            subject_line = next(line for line in content.splitlines() if line.lower().startswith("subject"))
            subject = subject_line.split(":", 1)[1].strip()

            body_lines = [line for line in content.splitlines() if not line.lower().startswith("subject")]
            body = "\n".join(body_lines).replace("Body:", "").strip()

            return subject, body

        except Exception as e:
            logger.error(f"❌ Failed to generate email via LLM for lead {lead.get('email')}: {e}")
            return "Introducing Newton AI", "Hi, I’d love to tell you more about Newton AI..."

    def send_cold_emails(self):
        updated = False
        for lead in self.leads:
            if lead.get("status") != "new":
                logger.debug(f"🔁 Skipping {lead.get('email')} - status: {lead.get('status')}")
                continue

            recipient_email = lead.get("email")
            if not recipient_email:
                logger.warning(f"❌ Skipping lead with no email: {lead}")
                continue

            logger.info(f"📤 Generating email for: {recipient_email}")
            subject, body = self._generate_email_llm(lead)

            success = send_email(recipient_email, subject, body)
            if success:
                lead["status"] = "contacted"
                logger.info(f"✅ Email sent to {recipient_email}")
            else:
                lead["status"] = "failed"
                logger.error(f"❌ Failed to send email to {recipient_email}")

            updated = True

        if updated:
            self._save_leads()

        return updated
