dev:
	cd weather/ && python3 -m uvicorn main:app --reload --port=8001
bot:
	cd weather/ && python3 bot.py
install:
	poetry install