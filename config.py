import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI configuration
OPENAI_CONFIG = {
    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "api_key": os.getenv("OPENAI_API_KEY", "your_default_api_key_here"),
    "api_type": os.getenv("OPENAI_API_TYPE", "azure"),
    "base_url": os.getenv("OPENAI_API_BASE", "https://newton-aoi.openai.azure.com/"),
    "api_version": os.getenv("OPENAI_API_VERSION", "2024-08-01-preview")
}
CALENDLY_LINK = os.getenv("CALENDLY_LINK", "https://calendly.com/demo/30min")
