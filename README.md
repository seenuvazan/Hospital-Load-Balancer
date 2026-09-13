# Hospital Load Balancer

A pure software-based intelligent system that balances digital hospital traffic across multiple backend servers while prioritizing emergencies and maintaining high availability.

## What the project does

- Distributes incoming `patient`, `doctor`, and `emergency` requests across multiple servers.
- Prioritizes traffic with `Emergency > Doctor > Patient`.
- Uses a least-load + emergency-override scoring strategy.
- Prevents overload by rejecting servers that would exceed safe capacity.
- Shows live server load, system health, requests, patients, and routing logs in a demo portal.

## Project structure

```text
hospital_lb/
  data.py
  engine.py
  models.py
  store.py
database/
  schema.sql
static/
  app.js
  index.html
  styles.css
tests/
  test_engine.py
app.py
README.md
```

## Problem statement

Hospital digital systems like appointment booking, ICU monitoring, lab reports, and emergency alerts can become overloaded during peak hours. This project demonstrates how a smart software layer can route requests before those systems fail or slow down.

## Core innovation

Priority-based intelligent load balancing:

- `Emergency` requests get an emergency override and the strongest routing preference.
- `Doctor` requests receive medium priority and prefer clinical servers.
- `Patient` requests are handled normally and prefer patient portal servers.

## How the system works

1. A request enters from the emergency module, doctor panel, or patient panel.
2. The load analyzer checks server health, load ratio, available capacity, and latency.
3. The priority engine assigns a priority score.
4. The smart router selects the best-fit server using least-load + emergency override.
5. A routing log is created for the admin dashboard.

## Portal features

- Admin dashboard for server health, live load, and system monitoring
- Doctor panel for medium-priority requests like EHR access and lab reports
- Patient panel for normal-priority requests like appointments
- Emergency module for fast-track routing that bypasses regular flow

## Database design

The project includes a PostgreSQL-style schema with these core tables:

- `requests` → `request_id`, `type`, `priority`, `status`
- `servers` → `server_id`, `load`, `status`
- `patients` → `patient_id`, `condition_level`
- `logs` → routing decisions and chosen server

See [database/schema.sql](/d:/genesis/database/schema.sql).

## Run locally

```bash
python app.py
```

Open `http://127.0.0.1:8000` in your browser.

## Run tests

```bash
python -m unittest discover -s tests
```

## Future ideas

- Add ambulance distance and location-aware routing
- Persist hospitals and allocations in a database
- Add authentication for hospital admins
- Show charts for load trends over time
