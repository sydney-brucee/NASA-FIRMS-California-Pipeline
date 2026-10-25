"""Load cleaned FIRMS detections into a local SQLite database."""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Literal
from src.clean import clean_from_raw

DEFAULT_DB_PATH = "data/firms.db"

def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection, creating the parent directory if needed."""
    Path(db_path).parent.mkdir(parents=False, exist_ok=True)
    return sqlite3.connect(db_path)

def load_to_sqlite(
        df: pd.DataFrame,
        db_path: str = DEFAULT_DB_PATH,
        table_name: str = "detections",
        if_exists: Literal["fail", "replace", "append"] = "replace",
) -> None:
    """Load a cleaned DataFrame into SQLite.
    
    if_exists: 'replace', 'append', or 'fail'
    """
    conn = get_connection(db_path)
    try:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    finally:
        conn.close()

def create_views(db_path: str = DEFAULT_DB_PATH, views_path: str = "sql/views.sql") -> None:
    """Create analytics views from the SQL file."""
    sql = Path(views_path).read_text(encoding="utf-8")
    conn = get_connection(db_path)
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()
    print(f"Created views from {views_path}")

def build_database(
        raw_dir: str = "data/raw",
        db_path: str = DEFAULT_DB_PATH,
) -> None:
    """Clean raw data and load it into SQLite."""
    print("Cleaning raw data...")
    df = clean_from_raw(raw_dir)
    print(f"Cleaned {len(df)} rows")

    print(f"Loading into {db_path}")
    load_to_sqlite(df, db_path=db_path, if_exists="replace")

    print("Creating views...")
    create_views(db_path=db_path)
    print("Done.")

if __name__ == "__main__":
    build_database()