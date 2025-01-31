import os

# Настройки OpenAI
OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Настройки Google Search
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CX = os.getenv("GOOGLE_CX", "")

# Настройки новостей
ITMO_NEWS_RSS = "https://news.itmo.ru/ru/rss/"