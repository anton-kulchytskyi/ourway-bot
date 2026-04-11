import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_URL: str = os.getenv("API_URL", "http://localhost:8000")
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
DEFAULT_LOCALE: str = os.getenv("DEFAULT_LOCALE", "en")
BOT_USERNAME: str = os.getenv("BOT_USERNAME", "ourway_tasks_bot")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
