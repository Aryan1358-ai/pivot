# Pivot 🔔

Pivot is a real-time stock price alert system. Users set price thresholds for stocks and get notified automatically when the market crosses them.

---

## Architecture Overview

```
[ yfinance API ]
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
[ TriggeredAlert saved to PostgreSQL ]

[ Client App ]
      │
      ▼  (HTTP + JWT)
[ Django REST API ] ──► (Reads prices from Redis, rules/alerts from PostgreSQL)
```

The producer/Kafka/consumer pipeline runs independently from the Django API — they only share PostgreSQL and Redis. This is the core of the decoupled, event-driven design.

---

## Tech Stack

| Technology | Why |
|------------|-----|
| **Django + DRF** | Serializers and ViewSets for clean API design; simplejwt for JWT authentication |
| **Apache Kafka** | Decouples price ingestion from alert checking — thousands of price updates per minute don't create load on the alert logic |
| **Redis** | Caches live stock prices for fast reads, avoiding repeated yfinance API calls |
| **PostgreSQL** | Relational storage for users, alert rules, and triggered alerts — relationships between these models make a relational DB the right fit |
| **Docker** | Runs Kafka, Redis, and PostgreSQL locally in isolated containers |

---

## Features

- Users can register and authenticate via JWT
- Create, view, update, and delete personal stock alert rules
- Set a price threshold and condition (above/below) per stock symbol
- Background Kafka consumer continuously monitors prices and fires alerts
- Triggered alerts are persisted to the database and queryable via API
- Live stock prices served from Redis cache via a dedicated endpoint
- Email notification sent to user when a price alert is triggered
---

## How to Run Locally

**Prerequisites:** Python 3.10+, Docker, Docker Compose

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/pivot.git
cd pivot

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Docker containers (Postgres, Redis, Kafka)
docker-compose up -d

# 5. Run migrations
python manage.py migrate

# 6. Start the Django API server
python manage.py runserver

# 7. In a second terminal — run the Kafka producer (fetches prices + publishes events)
python manage.py shell
>>> from market_alerts.producer import run_price_producer
>>> run_price_producer()

# 8. In a third terminal — run the alert consumer
python manage.py run_alert_checker
```

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

## Future Improvements

- **Alert re-arming + cooldown** — right now alerts deactivate after firing; a production version would re-arm once the price recovers, with a configurable cooldown period to prevent spam
- **WebSocket live dashboard** — use Django Channels to push live price updates to a frontend dashboard in real time
- **Frontend interface** — a React dashboard where users can manage watchlists, set alert rules, and see triggered alerts visually
- **Celery for scheduled price fetching** — replace the manual producer script with a Celery beat task that automatically fetches prices on a schedule

---

## Author

Aryan — BTech Final Year, Mumbai  
[LinkedIn](www.linkedin.com/in/aryan-kasar-571923381) | [GitHub](https://github.com/Aryan1358-ai)