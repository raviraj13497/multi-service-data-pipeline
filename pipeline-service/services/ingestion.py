import httpx
import logging
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from models.customer import Customer

logger = logging.getLogger(__name__)

MOCK_SERVER_URL = "http://mock-server:5000/api/customers"

def ingest_data(db: Session) -> int:
    page: int = 1
    limit: int = 50  
    total_processed: int = 0

    try:
        with httpx.Client(timeout=15.0) as client:
            while True:
                logger.info(f"Fetching page {page} limit {limit} from mock server")
                response = client.get(f"{MOCK_SERVER_URL}?page={page}&limit={limit}")
                response.raise_for_status()
                payload = response.json()
                
                data = payload.get("data", [])
                if not data:
                    break
                
                records = []
                for item in data:
                    records.append({
                        "customer_id": item["customer_id"],
                        "first_name": item["first_name"],
                        "last_name": item["last_name"],
                        "email": item["email"],
                        "phone": item.get("phone"),
                        "address": item.get("address"),
                        "date_of_birth": datetime.datetime.strptime(item["date_of_birth"], "%Y-%m-%d").date() if item.get("date_of_birth") else None,
                        "account_balance": float(item["account_balance"]) if item.get("account_balance") else None,
                        "created_at": datetime.datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")) if item.get("created_at") else None
                    })
                
                if not records:
                    break
                
                stmt = insert(Customer).values(records)
                
                update_dict = {
                    col.name: getattr(stmt.excluded, col.name) 
                    for col in Customer.__table__.columns 
                    if col.name != "customer_id"
                }
                
                upsert_stmt = stmt.on_conflict_do_update(
                    index_elements=['customer_id'],
                    set_=update_dict
                )
                
                db.execute(upsert_stmt)
                db.commit()
                
                total_processed += len(records)  # type: ignore
                logger.info(f"Successfully processed {len(records)} records from page {page}")

                total_in_source = int(payload.get("total", 0))
                current_coverage = page * limit  # type: ignore
                
                if current_coverage >= total_in_source:
                    break
                    
                page += 1  # type: ignore
                
        return total_processed
        
    except httpx.HTTPError as he:
        logger.error(f"HTTP Communication Error during ingestion: {str(he)}")
        db.rollback()
        raise Exception("Failed to fetch data from mock server.") from he
    except Exception as e:
        logger.error(f"Database/Ingestion Engine Error: {str(e)}")
        db.rollback()
        raise e
