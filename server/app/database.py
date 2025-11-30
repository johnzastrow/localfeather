"""
Local Feather - Database Connection and Session Management

Provides database connection handling for both MariaDB and SQLite.
"""

import os
import configparser
from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import Pool
from contextlib import contextmanager
import logging

from app.models import Base

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration manager"""

    def __init__(self, config_path: str = None):
        """
        Initialize database configuration.

        Args:
            config_path: Path to config.ini file. If None, uses default location.
        """
        if config_path is None:
            # Look for config.ini in database directory
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../database/config.ini'
            )

        self.config = configparser.ConfigParser()

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Database config not found at {config_path}. "
                f"Copy config.example.ini to config.ini and update settings."
            )

        self.config.read(config_path)

    def get_database_url(self, use_dev: bool = False) -> str:
        """
        Get SQLAlchemy database URL.

        Args:
            use_dev: If True, use development SQLite database

        Returns:
            Database connection URL
        """
        if use_dev and 'database_dev' in self.config:
            sqlite_path = self.config.get('database_dev', 'sqlite_path', fallback=None)
            if sqlite_path:
                # Convert relative path to absolute
                base_dir = os.path.dirname(os.path.dirname(__file__))
                db_path = os.path.join(base_dir, sqlite_path)
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                return f"sqlite:///{db_path}"

        # MariaDB/MySQL connection
        db_config = self.config['database']
        return (
            f"mysql+pymysql://{db_config['username']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            f"?charset=utf8mb4"
        )

    def get_pool_config(self) -> dict:
        """Get connection pool configuration"""
        db_config = self.config['database']
        return {
            'pool_size': db_config.getint('pool_size', fallback=10),
            'max_overflow': db_config.getint('max_overflow', fallback=20),
            'pool_recycle': db_config.getint('pool_recycle', fallback=3600),
            'pool_pre_ping': db_config.getboolean('pool_pre_ping', fallback=True),
        }


class Database:
    """Database connection manager"""

    def __init__(self, config_path: str = None, use_dev: bool = False, echo: bool = False):
        """
        Initialize database connection.

        Args:
            config_path: Path to config.ini file
            use_dev: Use development SQLite database
            echo: Enable SQL query logging
        """
        self.config = DatabaseConfig(config_path)
        self.database_url = self.config.get_database_url(use_dev)
        self.use_dev = use_dev

        # Create engine
        engine_kwargs = {
            'echo': echo,
            'future': True,
        }

        # Add connection pool settings for MariaDB
        if not use_dev:
            engine_kwargs.update(self.config.get_pool_config())

        self.engine = create_engine(self.database_url, **engine_kwargs)

        # Configure SQLite for better concurrency
        if use_dev:
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        logger.info(f"Database initialized: {self.database_url.split('@')[-1] if '@' in self.database_url else 'SQLite'}")

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.

        Usage:
            with db.session_scope() as session:
                user = session.query(User).first()
                ...
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def health_check(self) -> bool:
        """
        Check if database connection is working.

        Returns:
            True if database is accessible, False otherwise
        """
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database instance (initialized by Flask app)
db: Database = None


def init_db(config_path: str = None, use_dev: bool = False, echo: bool = False) -> Database:
    """
    Initialize the global database instance.

    Args:
        config_path: Path to config.ini file
        use_dev: Use development SQLite database
        echo: Enable SQL query logging

    Returns:
        Database instance
    """
    global db
    db = Database(config_path, use_dev, echo)
    return db


def get_db() -> Database:
    """
    Get the global database instance.

    Returns:
        Database instance

    Raises:
        RuntimeError: If database not initialized
    """
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db


def get_session() -> Session:
    """
    Get a new database session (for Flask dependency injection).

    Yields:
        SQLAlchemy Session
    """
    session = get_db().get_session()
    try:
        yield session
    finally:
        session.close()


# Flask-SQLAlchemy style query helper
def query_one_or_404(session: Session, model, **filters):
    """
    Query for a single record or raise 404.

    Args:
        session: Database session
        model: SQLAlchemy model class
        **filters: Filter criteria

    Returns:
        Model instance

    Raises:
        HTTPException: 404 if not found
    """
    from werkzeug.exceptions import NotFound

    result = session.query(model).filter_by(**filters).first()
    if result is None:
        raise NotFound(f"{model.__name__} not found")
    return result
