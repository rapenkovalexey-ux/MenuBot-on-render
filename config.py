import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "alexrap83@mail.ru")

# Payment
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")
SUBSCRIPTION_PRICE_RUB = 299

# Limits
FREE_MAX_DAYS = 3
TRIAL_DAYS = 10
TRIAL_MAX_DAYS = 31

# Groq — актуальная модель
GROQ_MODEL = "llama-3.3-70b-versatile"

# --- База данных ---
# Turso (продакшн на Koyeb): задайте TURSO_DATABASE_URL и TURSO_AUTH_TOKEN
# SQLite (локальная разработка): переменные Turso не задавать
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "")  # libsql://db-name.turso.io
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

USE_TURSO = bool(TURSO_DATABASE_URL and TURSO_AUTH_TOKEN)

# Fallback для локальной разработки
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./menu_bot.db")
