"""
config.py
----------
Loads configuration (currently just the Gemini API key) from a local
.env file. Keeping this in one place means every other module just does
`from utils.config import GEMINI_API_KEY` and doesn't care where it came
from.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. Create a .env file in the project root "
        "(see .env.example) with GEMINI_API_KEY=your_key_here"
    )
