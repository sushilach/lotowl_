import os
import sys
from urllib.parse import urlparse

import pymysql


def normalize_mysql_url(raw_url: str) -> str:
    if raw_url.startswith("mysql+pymysql://"):
        return "mysql://" + raw_url[len("mysql+pymysql://") :]
    return raw_url


def main() -> int:
    database_url = os.environ.get("DATABASE_URL") or os.environ.get("MYSQL_URL") or os.environ.get("MYSQL_PUBLIC_URL")

    if not database_url:
        print("ERROR: Missing DATABASE_URL (or MYSQL_URL / MYSQL_PUBLIC_URL).")
        return 1

    mysql_url = normalize_mysql_url(database_url)
    parsed = urlparse(mysql_url)

    if parsed.scheme != "mysql":
        print(f"ERROR: Expected mysql URL scheme, got: {parsed.scheme}")
        return 1

    host = parsed.hostname
    port = parsed.port or 3306
    user = parsed.username
    password = parsed.password
    database = parsed.path.lstrip("/")

    if not all([host, user, database]):
        print("ERROR: DATABASE_URL is missing host/user/database components.")
        return 1

    print("Connecting to MySQL...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"User: {user}")

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=10,
            read_timeout=10,
            write_timeout=10,
            ssl={"ssl": {}} if os.environ.get("MYSQL_USE_SSL", "true").lower() == "true" else None,
            cursorclass=pymysql.cursors.DictCursor,
        )
    except Exception as exc:
        print(f"ERROR: Connection failed: {exc}")
        return 2

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok")
            row = cur.fetchone()
            print(f"SELECT 1 result: {row}")

            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
            print(f"Tables found: {len(tables)}")
            for table in tables:
                print(table)

        print("SUCCESS: Database connection is working.")
        return 0
    except Exception as exc:
        print(f"ERROR: Query failed: {exc}")
        return 3
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
