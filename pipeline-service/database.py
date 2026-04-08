import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/customer_db"
    
    # Modern Pydantic v2 resolution pattern replacing `class Config`
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

# Applying production connection pooling enhancements
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,          
    max_overflow=10,       
    pool_timeout=30,       
    pool_recycle=1800,     
    pool_pre_ping=True     
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
