# prompts/__init__.py

from pathlib import Path

with open(Path(__file__).parent / "scoring_prompt_template.md", "r", encoding="utf-8") as f:
    scoring_prompt_template = f.read()

with open(Path(__file__).parent / "cold_email_prompt_template.md", "r", encoding="utf-8") as f:
    cold_email_prompt_template = f.read()
