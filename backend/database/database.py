from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.signal_models import Base
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Try to create database engine, but make it optional
try:
    # Use DATABASE_URL if provided, otherwise align default with API server
    # Using a relative path to backend folder for SQLite
    database_url = os.getenv("DATABASE_URL", "sqlite:///./trading_signals.db")
    
    # Configure engine based on database type
    if database_url.startswith('postgresql'):
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
            echo=False  # Set to True for debugging
        )
        logger.info("✅ PostgreSQL database engine created")
    else:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={"check_same_thread": False},  # SQLite specific
            echo=False  # Set to True for debugging
        )
        logger.info("✅ SQLite database engine created")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    DATABASE_AVAILABLE = True
    logger.info("✅ Database engine created successfully")
except Exception as e:
    logger.warning(f"⚠️ Database not available: {e}")
    logger.info("   System will run without database (signals won't be persisted)")
    engine = None
    SessionLocal = None
    DATABASE_AVAILABLE = False

def create_tables():
    """Create all database tables"""
    if not DATABASE_AVAILABLE:
        logger.warning("Database not available, skipping table creation")
        return
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        # Don't raise - allow system to continue without database

def get_db():
    """Dependency to get database session"""
    if not DATABASE_AVAILABLE or SessionLocal is None:
        # Return a mock session that does nothing
        class MockSession:
            def query(self, *args, **kwargs):
                return self
            def filter(self, *args, **kwargs):
                return self
            def all(self):
                return []
            def first(self):
                return None
            def add(self, *args, **kwargs):
                pass
            def commit(self):
                pass
            def rollback(self):
                pass
            def close(self):
                pass
        
        yield MockSession()
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables"""
    if not DATABASE_AVAILABLE:
        logger.warning("⚠️ Database not available - system will run without persistence")
        return
    
    create_tables()
    logger.info("Database initialized successfully")