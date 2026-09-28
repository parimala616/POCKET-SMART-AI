# PocketSmart AI

PocketSmart AI is a GenAI-powered budget and recommendation assistant.

It contains three main planners:

1. Home Interior Planner
2. Party Budget Planner
3. Jewelry Budget Planner

The Jewelry Planner can optionally accept an outfit image for multimodal AI analysis.

---

# Technology Stack

## Frontend

- React
- Vite
- JavaScript
- CSS
- Lucide React

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT authentication

## AI

- Google Gemini
- google-genai SDK

---

# Project Structure

```text
pocketsmart-ai/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── ai.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── links.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── tests/
│   │   ├── test_fallback.py
│   │   └── test_health.py
│   │
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── styles.css
│   │
│   ├── .env.example
│   ├── index.html
│   └── package.json
│
├── .gitignore
└── README.md