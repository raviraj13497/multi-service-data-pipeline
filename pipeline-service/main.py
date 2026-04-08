import logging
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models.customer import Customer
from services.ingestion import ingest_data

# Create tables (Typically managed by Alembic in true production schemas)
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI Pipeline Service")

@app.post("/api/ingest")
def trigger_ingestion(db: Session = Depends(get_db)):
    """
    Triggers the ingestion of customer data from the mock server into PostgreSQL.
    """
    logger.info("Starting ingestion workflow")
    try:
        processed = ingest_data(db)
        logger.info(f"Ingestion successful. {processed} records processed.")
        return {"status": "success", "records_processed": processed}
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail="Ingestion subsystem failed. Check logs.")

@app.get("/api/customers")
def get_customers(
    page: int = Query(1, ge=1, description="Numerical Page Query Parameter"),
    limit: int = Query(10, ge=1, le=1000, description="Amount of Items per Payload Limit"),
    db: Session = Depends(get_db)
):
    """
    Retrieve paginated customers from the database.
    (Note: OFFSET logic provides baseline pagination. For massive DB datasets containing millions of rows, 
    Keyset Pagination/Cursor logic guarantees reliable non-degrading performance)
    """
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()
    
    # NOTE: The `.count()` forces a full table scan. 
    # For massive DB operations, consider removing exact total counts and implement streaming
    total = db.query(Customer).count()
    return {
        "data": customers,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a singular customer strictly by their primary ID.
    """
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer target missing")
    return customer
