# Network Latency Tracer & Outage Logger

## Overview

Network Latency Tracer & Outage Logger is a network monitoring application designed to track host availability, measure latency performance, detect outages, and generate reliability reports.

The system continuously monitors configured network targets using ICMP ping requests, stores monitoring data in an SQLite database, analyses network performance, and provides a web dashboard for viewing real-time statistics, latency trends, packet loss, and outage history.

The application is built using a **FastAPI backend** with a **React frontend dashboard**.

---

# Features

## Network Monitoring

- Continuously monitor multiple hosts
- Measure round-trip latency (RTT)
- Track successful and failed ping attempts
- Record packet loss
- Maintain latency history

## Dynamic Host Management

- Add new hosts from the dashboard
- Remove monitored hosts
- Enable or disable monitoring targets
- Automatically detect newly added hosts

## Outage Detection

- Detect hosts experiencing failures
- Track outage start and recovery time
- Calculate outage duration
- Store outage history

## Analytics

- Calculate:
  - Average latency
  - Minimum and maximum latency
  - Packet loss percentage
  - Uptime percentage
  - Reliability statistics
  - Mean Time Between Failures (MTBF)
  - Mean Time To Recovery (MTTR)

## Dashboard

The web dashboard provides:

- Fleet monitoring summary
- Host status overview
- Latency charts
- Packet loss charts
- Outage history
- Host performance details

## Reporting

Generate monitoring reports including:

- Network reliability summaries
- Host performance reports
- Latency statistics
- Outage records

---

# Technologies Used

## Backend

- Python
- FastAPI
- Uvicorn
- ICMPlib
- SQLite
- Pandas
- Plotly
- Matplotlib

## Frontend

- React
- Vite
- Axios
- Chart libraries
- CSS

## Database

- SQLite

---

# System Architecture

```
NetworkLatencyTracer/

│
├── backend/
│
│   ├── api/
│   │   ├── main.py
│   │   └── routes/
│   │
│   ├── monitoring/
│   │   ├── monitor.py
│   │   ├── ping_engine.py
│   │   ├── models.py
│   │   └── config.py
│   │
│   ├── database/
│   │   └── latency.db
│   │
│   ├── reporting/
│   │
│   ├── analytics/
│   │
│   └── requirements.txt
│
│
├── frontend/
│
│   ├── src/
│   │
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── services/
│
└── README.md
```

---

# How It Works

1. Hosts are added through the dashboard.
2. Host information is stored in SQLite.
3. The monitoring engine loads active hosts.
4. ICMP ping requests are sent periodically.
5. Latency and availability results are recorded.
6. The outage detector analyses failed requests.
7. Analytics processes historical data.
8. The dashboard displays current network health.

---

# Installation

## Backend Setup
Open terminal
Navigate to the backend folder:

```bash
cd backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn api.main:app --reload
```

The API will run at:

```
http://127.0.0.1:8000
```

---

## Frontend Setup
Open another terminal
Navigate to the frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the React application:

```bash
npm run dev
```

The dashboard will run at:

```
http://localhost:5173
```

---

# API Endpoints

## Hosts

```
GET    /api/hosts
POST   /api/hosts
DELETE /api/hosts/{id}
PATCH  /api/hosts/{id}/toggle
```

## Analytics

```
GET /api/analytics/summary
GET /api/analytics/full
GET /api/analytics/host/{host_ip}
```

## Reports

```
GET /api/reports
GET /api/reports/pdf
GET /api/reports/csv
```

---

# Team Structure

- Project Manager
- Network Monitoring Developer
- Outage Detection Developer
- Database Developer
- Backend API Developer
- Frontend Dashboard Developer
- Analytics Developer
- Reporting Developer
- Testing Engineer
- Documentation Engineer

---

# Future Improvements

Possible future enhancements:

- User authentication
- Email/SMS outage notifications
- More advanced alert rules
- Network device discovery
- Historical performance forecasting
- PostgreSQL database support
- Docker deployment
- Cloud hosting

---

# License

This project was developed as part of a network monitoring and reliability analysis system.
