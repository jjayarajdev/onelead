"""Base database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config_loader import config

# Create database directory if it doesn't exist
db_path = Path(config.database_path)
db_path.parent.mkdir(parents=True, exist_ok=True)

# Create engine
DATABASE_URL = f"sqlite:///{config.database_path}"
engine = create_engine(
    DATABASE_URL,
    echo=config.get('database.echo', False),
    connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session (for dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
