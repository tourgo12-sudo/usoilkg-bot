import requests, os
TOKEN = os.getenv("BOT_TOKEN")
requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={"chat_id": "@xauusdakyl", "text": "✅ ТЕСТ: Бот иштеп жатат! 🛢️ US crude oil $91.85 | Рынок ачылганда 100% сигнал келет.", "parse_mode": "HTML"}, timeout=20)
