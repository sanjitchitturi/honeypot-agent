import os
from typing import Dict

# API Configuration
HONEYPOT_API_KEY = os.getenv("HONEYPOT_API_KEY", "hackathon_secret_key_12345")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model Configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2000
TEMPERATURE = 0.7

# Scam Detection Confidence Threshold
SCAM_CONFIDENCE_THRESHOLD = 0.6

# Persona Templates for believable responses
VICTIM_PERSONAS = {
    "elderly": {
        "name": "Margaret",
        "age": 68,
        "traits": "trusting, not tech-savvy, worried about money, easily confused",
        "style": "polite, asks many questions, types slowly with occasional typos"
    },
    "young_professional": {
        "name": "Rahul",
        "age": 28,
        "traits": "busy, somewhat skeptical but curious, wants quick solutions",
        "style": "casual, uses some slang, moderately tech-aware"
    },
    "desperate": {
        "name": "Priya",
        "age": 35,
        "traits": "financially stressed, looking for opportunities, hopeful",
        "style": "eager, asks about details, wants to believe it's real"
    }
}

# Intelligence extraction patterns
INTELLIGENCE_PATTERNS = {
    "phone_number": r'\+?\d{10,15}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
    "bank_account": r'\b\d{9,18}\b',
    "ifsc_code": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
    "upi_id": r'\b[\w\.\-]+@[\w]+\b',
    "url": r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
}