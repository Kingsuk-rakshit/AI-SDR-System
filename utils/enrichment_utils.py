# utils/enrichment_utils.py

import random
from utils.logger import get_logger

logger = get_logger("EnrichmentUtils")

COMMON_PATTERNS = [
    "{first}@{domain}",
    "{first}.{last}@{domain}",
    "{first_initial}{last}@{domain}",
    "{first}{last}@{domain}"
]

def generate_dummy_email(name, domain):
    parts = name.strip().lower().split()
    if not parts or not domain:
        return f"contact@example.com"
    
    first = parts[0]
    last = parts[1] if len(parts) > 1 else "team"
    pattern = random.choice(COMMON_PATTERNS)

    email = pattern.format(
        first=first,
        last=last,
        first_initial=first[0],
        domain=domain
    )

    logger.debug(f"Generated email: {email}")
    return email

def enrich_lead(lead):
    """
    Adds dummy email and LinkedIn profile for testing/demo.
    """
    name = lead.get("name", "")
    domain = lead.get("domain", "example.com")

    if not lead.get("email"):
        lead["email"] = generate_dummy_email(name, domain)

    lead["linkedin"] = f"https://linkedin.com/in/{name.lower().replace(' ', '')}"
    lead["enriched"] = True

    logger.info(f"Enriched lead: {lead['name']} → {lead['email']}")
    return lead
