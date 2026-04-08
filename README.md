# Customer Data Pipeline System

A production-ready multi-service data pipeline built using **Flask, FastAPI, PostgreSQL, and Docker**.

This system simulates real-world data ingestion where data is fetched from an external service, processed, and stored in a database.

## Architecture

### Components:

1. **Flask Mock Server (`mock-server`)**
   - Runs on **port 5001 (host) / 5000 (container)**
   - Serves customer data from JSON
   - Supports pagination

2. **FastAPI Pipeline Service (`pipeline-service`)**
   - Runs on **port 8000**
   - Fetches data from Flask API
   - Handles pagination automatically
   - Performs UPSERT into PostgreSQL
   - Exposes APIs to query stored data

3. **PostgreSQL (`postgres`)**
   - Runs on **port 5432**
   - Stores customer records


## Features

- Multi-service Docker architecture
- Pagination support (Flask & FastAPI)
- Automatic data ingestion pipeline
- UPSERT logic (insert/update)
- SQLAlchemy ORM integration
- Structured logging for debugging & observability
- Error handling for API and database operations

## Setup & Run

Start all services:

```bash
docker-compose up -d --build
```

API Testing

1. Test Flask Mock Server
```bash
curl "http://localhost:5001/api/customers?page=1&limit=5"
```

2. Trigger Data Ingestion

Fetches all paginated data from Flask and stores in PostgreSQL:
```bash
curl -X POST http://localhost:8000/api/ingest
```

3. Fetch Data from Database (FastAPI)
```bash
curl "http://localhost:8000/api/customers?page=1&limit=5"
```

4. Fetch Single Customer
```bash
curl http://localhost:8000/api/customers/C-001
```

5. Stopping the Project
When you're finished, you can cleanly stop and remove the containers by running:

```bash
docker-compose down
```
