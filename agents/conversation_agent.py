# agents/conversation_agent.py

import json
from pathlib import Path
import openai
from config import OPENAI_CONFIG
from utils.logger import get_logger
from autogen import ConversableAgent

logger = get_logger("ConversationAgent")

# Set OpenAI Azure config globally (important)
openai.api_key = OPENAI_CONFIG["api_key"]
openai.base_url = OPENAI_CONFIG["base_url"]
openai.api_type = OPENAI_CONFIG["api_type"]
openai.api_version = OPENAI_CONFIG["api_version"]

# Load product context
try:
    with open("prompts/newton_product_info.md", "r", encoding="utf-8") as f:
        PRODUCT_CONTEXT = f.read()
except FileNotFoundError:
    logger.warning("⚠️ newton_product_info.md not found. Using empty context.")
    PRODUCT_CONTEXT = ""

REPLY_CLASSIFIER_PROMPT = """
You are a helpful SDR assistant for Newton AI, a no-code ML tool for data analysts.

Based on the following reply, classify the lead's interest level and next step.
Reply: "{reply}"

Context:
{context}

Return a JSON with:
- "status": one of ["interested", "not_interested", "book_meeting", "reply_received", "unclear"]
- "reason": short explanation
"""

class ConversationAgent:
    def __init__(self, lead_source_path="data/leads.json"):
        self.lead_source_path = Path(lead_source_path)
        self.leads = self._load_leads()

        # Setup ConversableAgent with Azure OpenAI config
        try:
            self.llm_agent = ConversableAgent(
                name="ReplyClassifier",
                llm_config={
                    "config_list": [
                        {
                            "api_key": OPENAI_CONFIG["api_key"],
                            "base_url": OPENAI_CONFIG["base_url"],
                            "api_type": OPENAI_CONFIG["api_type"],
                            "api_version": OPENAI_CONFIG["api_version"],
                            "model": OPENAI_CONFIG["model"]
                        }
                    ]
                }
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize ConversableAgent: {e}")
            raise

    def _load_leads(self):
        if self.lead_source_path.exists():
            try:
                with open(self.lead_source_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("⚠️ Failed to decode leads JSON.")
        return []

    def _save_leads(self):
        with open(self.lead_source_path, "w", encoding="utf-8") as f:
            json.dump(self.leads, f, indent=2)

    def _parse_llm_response(self, result, email):
        try:
            parsed = json.loads(result)
            status = parsed.get("status", "unclear")
            reason = parsed.get("reason", "No reason provided.")
        except Exception as e:
            logger.error(f"❌ Failed to parse LLM JSON for {email}: {e}")
            logger.debug(f"🧠 Raw LLM output:\n{result}")
            status = "unclear"
            reason = "LLM response could not be parsed."
        return status, reason

    def _update_lead_status(self, email, status, reason):
        for lead in self.leads:
            if lead.get("email") == email:
                lead["status"] = status
                lead["llm_reason"] = reason
                if status in ["interested", "book_meeting"]:
                    lead["sales_stage"] = "consideration"
                logger.info(f"🔍 {lead['name']} ({email}) → Status: {status} | Reason: {reason}")
                break

    def _classify_reply(self, email, reply_text):
        prompt = REPLY_CLASSIFIER_PROMPT.format(reply=reply_text, context=PRODUCT_CONTEXT)
        try:
            response = self.llm_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
            result = response.get("content") if isinstance(response, dict) else str(response)
        except Exception as e:
            logger.error(f"❌ Error during reply classification for {email}: {e}")
            result = '{"status": "unclear", "reason": "LLM error occurred."}'
        return self._parse_llm_response(result, email)

    def simulate_reply_handling(self, simulated_replies):
        for reply in simulated_replies:
            email = reply["email"]
            message = reply["reply"]
            logger.info(f"🧠 Simulating reply classification for {email}")
            status, reason = self._classify_reply(email, message)
            self._update_lead_status(email, status, reason)
        self._save_leads()

    def process_live_reply(self, email, reply_text):
        logger.info(f"📨 Received new reply from {email}")
        status, reason = self._classify_reply(email, reply_text)
        self._update_lead_status(email, status, reason)
        self._save_leads()
        return status, reason

    def get_reply_summary(self):
        return [
            {
                "name": lead["name"],
                "email": lead["email"],
                "status": lead.get("status", "unknown"),
                "reason": lead.get("llm_reason", "N/A")
            }
            for lead in self.leads
            if lead.get("status") in ["interested", "reply_received", "book_meeting", "not_interested"]
        ]

    def get_interested_leads(self):
        return [lead for lead in self.leads if lead.get("status") == "book_meeting"]
