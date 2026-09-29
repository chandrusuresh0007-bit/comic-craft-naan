# PocketSmart AI

PocketSmart AI is a budget-aware AI recommendation assistant for:

- Home Interior Planning
- Party Planning
- Jewelry Planning

The application uses:

- FastAPI
- Jinja2
- HTML/CSS/JavaScript
- SQLite
- SQLAlchemy
- JWT-backed sessions
- Gemini AI
- Optional multimodal image input for the Jewelry Planner

---

# Features

## Authentication

- Register
- Login
- Logout
- Session information
- Personalized session data

## Home Planner

Users provide:

- Budget
- Rooms
- Interior style
- Priorities
- Notes

The system generates:

- Furniture
- Decor
- Lighting
- Storage
- Budget allocation
- Spending tips

## Party Planner

Users provide:

- Budget
- Guest count
- Event type
- City
- Venue preference
- Food preference
- Notes

The system generates:

- Venue ideas
- Food recommendations
- Decoration
- Entertainment
- Budget allocation
- Spending tips

## Jewelry Planner

Users provide:

- Budget
- Occasion
- Style
- Metal preference
- Optional outfit image
- Notes

The system generates:

- Earrings
- Necklace
- Bracelet
- Ring
- Other jewelry suggestions
- Styling tips

---

# AI

The application supports Google Gemini through the Gemini REST API.

Set:

GEMINI_API_KEY=your-api-key

in `.env`.

The model is configurable:

GEMINI_MODEL=gemini-1.5-flash

If no Gemini API key is provided, PocketSmart AI automatically uses its local fallback recommendation engine.

This means the application can still be run and tested without an AI API key.

---

# Installation

## 1. Install Python

Use Python 3.11 or newer.

Check:

python --version

---

## 2. Open the project

Open the `pocketsmart-ai` folder in VS Code.

---

## 3. Create a virtual environment

Windows PowerShell:

python -m venv .venv

Activate:

.venv\Scripts\Activate.ps1

---

## 4. Install dependencies

pip install --upgrade pip

pip install -r requirements.txt

---

# Environment configuration

Copy:

.env.example

to:

.env

Windows PowerShell:

Copy-Item .env.example .env

Then edit `.env`.

Example:

GEMINI_API_KEY=your-gemini-api-key

Use long random values for:

SESSION_SECRET

JWT_SECRET

---

# Run the application

From the project root:

uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000

---

# API documentation

FastAPI Swagger UI:

http://127.0.0.1:8000/docs

ReDoc:

http://127.0.0.1:8000/redoc

Health check:

http://127.0.0.1:8000/health

---

# Application pages

Home:

/

Login:

/login

Register:

/register

Dashboard:

/dashboard

Home Planner:

/planner/home

Party Planner:

/planner/party

Jewelry Planner:

/planner/jewelry

---

# API endpoints

Authentication:

POST /api/register

POST /api/login

POST /api/logout

POST /api/token

GET /api/session-info

GET /api/session-data

Planning:

POST /api/generate-home

POST /api/generate-party

POST /api/generate-jewelry

History:

GET /api/history

GET /api/recommendations-details/{recommendation_id}

System:

GET /health

GET /startup

---

# Testing

Run:

pytest -q

---

# Gemini image support

The Jewelry Planner accepts:

- JPEG
- PNG
- WEBP

Maximum size:

5 MB

The image is sent as an inline multimodal part to Gemini.

If the Gemini API is unavailable, the application automatically falls back to text-based recommendations.

---

# Important marketplace behavior

PocketSmart AI does not pretend to have live marketplace inventory.

Recommendation cards generate search links for services such as:

- Amazon
- Flipkart
- IKEA
- Swiggy
- Zomato
- OYO

Prices shown by the recommendation engine are estimates.

For production use, authorized marketplace APIs should be integrated if live prices or inventory are required.

---

# GitHub

Initialize:

git init

Add files:

git add .

Commit:

git commit -m "Initial PocketSmart AI project"

Create a GitHub repository and then:

git branch -M main

git remote add origin YOUR_GITHUB_REPOSITORY_URL

git push -u origin main

---

# Production notes

Before production:

1. Use strong random SESSION_SECRET.
2. Use strong random JWT_SECRET.
3. Set COOKIE_SECURE=true.
4. Use HTTPS.
5. Replace SQLite with PostgreSQL for larger deployments.
6. Configure CORS with the real frontend domain.
7. Add rate limiting.
8. Add production logging.
9. Store uploaded images using secure object storage if persistent images are needed.
10. Use authorized marketplace APIs instead of scraping.
11. Monitor Gemini API usage and limits.

---

# Project architecture

app/
    main.py

    config.py

    database.py

    security.py

    models.py

    routes/
        auth.py
        pages.py
        planners.py

    services/
        catalog.py
        gemini.py

    templates/
        base.html
        index.html
        login.html
        register.html
        dashboard.html
        home_planner.html
        party_planner.html
        jewelry_planner.html

    static/
        css/
            style.css

        js/
            app.js
            planners.js

tests/
    test_api.py
