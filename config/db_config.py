import os
from urllib.parse import urlparse


def get_database_url() -> str:
    """Return the preferred database URL from environment variables.

    Priority for Railway deployments:
    1) DATABASE_URL (web service variable)
    2) MYSQL_URL (private internal Railway URL)
    3) MYSQL_PUBLIC_URL (public fallback)
    4) local sqlite fallback
    """
    return (
        os.environ.get("DATABASE_URL")
        or os.environ.get("MYSQL_URL")
        or os.environ.get("MYSQL_PUBLIC_URL")
        or "sqlite:///lotowl.db"
    )


def get_mysql_url_with_driver() -> str:
    """Normalize mysql URL for SQLAlchemy + PyMySQL usage."""
    db_url = get_database_url()
    if db_url.startswith("mysql://"):
        return db_url.replace("mysql://", "mysql+pymysql://", 1)
    return db_url


def get_mysql_settings() -> dict:
    """Return parsed connection settings from DATABASE_URL-style env vars."""
    db_url = get_database_url()
    parsed = urlparse(db_url)

    return {
        "scheme": parsed.scheme,
        "host": parsed.hostname,
        "port": parsed.port,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/") if parsed.path else None,
    }


def is_mysql_configured() -> bool:
    """True when database URL points to MySQL."""
    db_url = get_database_url()
    return db_url.startswith("mysql://") or db_url.startswith("mysql+pymysql://")
