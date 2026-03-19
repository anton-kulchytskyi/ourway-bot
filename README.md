# OurWay Bot

Telegram bot for OurWay — a family task manager with Kanban board and gamification.

## Tech Stack

- aiogram 3.x (Python 3.12)
- Communicates with ourway-backend via HTTP API

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## Deploy

Deployed on Railway. Every push to `main` triggers a new deployment.
