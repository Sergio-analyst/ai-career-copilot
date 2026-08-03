import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_URL = "https://www.linkedin.com/feed/"

SEARCH_KEYWORDS = "AI Automation Engineer"
SEARCH_LOCATIONS = [
    "Dubai",
    "Abu Dhabi",
]

PROFILE_DIR = "./browser_profile"

HEADLESS = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")