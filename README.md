# Pivot 🔔

Pivot is a real-time stock price alert system. Users set price thresholds for stocks and get notified automatically — via AI-generated, natural-language email alerts — when the market crosses them.

---

## Architecture Overview

```
[ yfinance API ]
      │
      ▼
[ Celery Beat ] ──► triggers every 60s
      │
      ▼
[ Python Producer ] ──► (Caches price in Redis)
      │
      ▼
[ Apache Kafka ]
      │
      ▼
[ Consumer ] ──► (Checks AlertRules in PostgreSQL)
      │
      ▼
[ Gemini API ] ──► generates natural-language alert message
      │
      ▼
[ TriggeredAlert saved to PostgreSQL ] + [ Email sent to user ]

[ React Frontend ]
      │
      ▼  (HTTP + JWT)
[ Django REST API ] ──► (Reads prices from Redis, rules/alerts from PostgreSQL)
```

The producer/Kafka/consumer pipeline runs independently from the Django API — they only share PostgreSQL and Redis. Celery Beat automates price fetching on a schedule, removing the need for any manual intervention. This is the core of the decoupled, event-driven design.

---

## Tech Stack

| Technology | Why |
|------------|-----|
| **Django + DRF** | Serializers and ViewSets for clean API design; simplejwt for JWT authentication |
| **Apache Kafka** | Decouples price ingestion from alert checking — thousands of price updates per minute don't create load on the alert logic |
| **Redis** | Caches live stock prices for fast reads, avoiding repeated yfinance API calls; also serves as the Celery broker |
| **PostgreSQL** | Relational storage for users, alert rules, and triggered alerts — relationships between these models make a relational DB the right fit |
| **Celery + Celery Beat** | Automates price fetching on a fixed schedule, replacing manual script runs with a production-style background task |
| **Google Gemini API** | Generates natural-language alert messages from structured trigger data via a constrained prompt, instead of a static template |
| **Docker** | Runs Kafka, Redis, and PostgreSQL locally in isolated containers |
| **React (CDN, no build step)** | Lightweight terminal-style dashboard for managing rules and viewing triggered alerts |

---

## Features

- Users can register and authenticate via JWT
- Create, view, update, and delete personal stock alert rules
- Set a price threshold and condition (above/below) per stock symbol
- Background Kafka consumer continuously monitors prices and fires alerts
- Triggered alerts are persisted to the database and queryable via API
- **AI-generated alert messages** — when an alert fires, a prompt-engineered call to the Gemini API converts the raw trigger data (symbol, condition, threshold, current price) into a clear, natural-language email, rather than a static string
- Live stock prices served from Redis cache via a dedicated endpoint
- Automatic price fetching every 60 seconds via Celery Beat — no manual scripts
- Minimal terminal-style frontend dashboard for managing rules and viewing alerts
- Real-time price monitoring via an event-driven Kafka pipeline, decoupling data ingestion from alert processing

---

## How to Run Locally

**Prerequisites:** Python 3.10+, Docker, Docker Compose

```bash
# 1. Clone the repo
git clone https://github.com/Aryan1358-ai/pivot.git
cd pivot

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file in the root folder (see .env.example)

# 5. Start Docker containers (Postgres, Redis, Kafka)
docker-compose up -d

# 6. Run migrations
python manage.py migrate

# 7. Start the Django API server
python manage.py runserver

# 8. In a second terminal — start the Kafka consumer
python manage.py run_alert_checker

# 9. In a third terminal — start the Celery worker
celery -A Pivot worker --loglevel=info --pool=solo

# 10. In a fourth terminal — start Celery Beat (price fetching scheduler)
celery -A Pivot beat --loglevel=info

# 11. In a fifth terminal — serve the frontend
cd frontend
python -m http.server 5500
# Visit http://localhost:5500
```

Prices are automatically fetched every 60 seconds via Celery Beat and published to Kafka. No manual producer script needed.

---

## API Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/token/` | No | Get JWT access + refresh tokens |
| POST | `/api/token/refresh/` | No | Refresh an expired access token |
| GET | `/api/alert-rules/` | Yes | List your alert rules |
| POST | `/api/alert-rules/` | Yes | Create a new alert rule |
| PUT/PATCH | `/api/alert-rules/<id>/` | Yes | Update an alert rule |
| DELETE | `/api/alert-rules/<id>/` | Yes | Delete an alert rule |
| GET | `/api/triggered-alerts/` | Yes | List your triggered alerts |
| GET | `/api/get_price/<symbol>/` | Yes | Get cached price for a stock symbol |

**Example request body for `POST /api/alert-rules/`:**
```json
{
    "stock_symbol": "RELIANCE.NS",
    "price_threshold": "2800.00",
    "condition": "BELOW"
}
```

---

## Testing & CI

The project includes a test suite covering:
- Authorization (a user cannot create or view another user's alert rules — protects against Broken Object Level Authorization)
- Alert condition logic (ABOVE / BELOW threshold checks)
- Redis cache hit/miss behavior (mocked, no live Redis dependency)

Tests run automatically on every push via **GitHub Actions** (`.github/workflows/ci.yml`).

```bash
python manage.py test market_alerts
```

---

## Future Improvements

- **Alert re-arming + cooldown** — currently alerts deactivate after firing; a production version would re-arm once the price recovers, with a configurable cooldown period to prevent spam
- **WebSocket live dashboard** — use Django Channels to push live price updates to the frontend in real time instead of polling
- **Deployment** — containerize the Django app itself and deploy the full stack (Railway/Render) for a live, publicly accessible URL
- **Real-time data provider** — swap yfinance for a WebSocket-based broker API (e.g. Zerodha Kite Connect) for true tick-by-tick pricing
- **Rate limiting** — add DRF throttling to protect public endpoints from abuse

---

## Author

Aryan — BTech Final Year, Mumbai
[LinkedIn](https://www.linkedin.com/in/aryan-kasar-571923381) | [GitHub](https://github.com/Aryan1358-ai)