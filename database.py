from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartfarm.db")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file or fallback")

connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test DB connection
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))  # Use text() for SQL statement
except Exception as e:
    raise Exception(f"Database connection failed: {str(e)}")