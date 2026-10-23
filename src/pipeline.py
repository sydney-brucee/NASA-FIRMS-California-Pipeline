"""Run the full pipeline: ingest → clean → load."""

from src.ingest import ingest_last_n_days
from src.load import build_database

def run(n_days: int = 30) -> None:
    print("=== Ingest ===")
    ingest_last_n_days(n_days)

    print("\n=== Clean & Load ===")
    build_database()

    print("\nPipeline complete.")

if __name__ == "__main__":
    run()