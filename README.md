# Data Pipeline Project

A production-ready multi-service data pipeline system utilizing Flask, FastAPI, PostgreSQL, and Docker.

## Architecture
1. **Flask Mock Server** (`mock-server`): Exposed on host port 5001 (internal 5000), serving mock customer data from JSON via a paginated API.
2. **FastAPI Pipeline Service** (`pipeline-service`): Runs on port 8000, fetching data from the Mock Server and upserting into the PostgreSQL database.
3. **Database** (`postgres`): Runs on port 5432.

## Setup & Run

Start all services securely in background:
```bash
docker-compose up -d --build
```

## Testing Endpoints

### 1. Test Mock Server
```bash
curl http://localhost:5001/api/customers?page=1&limit=5
```

### 2. Trigger Ingestion 
(Fetches data from mock-server and UPSERTS into PostgreSQL)
```bash
curl -X POST http://localhost:8000/api/ingest
```

### 3. Verify Ingestion via FastAPI
```bash
curl http://localhost:8000/api/customers?page=1&limit=5
```
