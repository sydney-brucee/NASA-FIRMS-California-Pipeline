"""NASA FIRMS live ingest for California wildfire detections.

Reads MAP_KEY from the FIRMS_MAP_KEY environment variable.
Saves raw CSV responses to data/raw/.
"""

import os
import pandas as pd
import requests
from io import StringIO
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv() # Loads FIRMS_MAP_KEY from .env
# If you prefer to set the key in the terminal instead, comment out the two lines above
# an run: $env:FIRMS_MAP_KEY = "your_key_here" (PowerShell)
# or: export FIRMS_MAP_KEY="your_key_here" (macOS/Linux)

# Approximate California bounding box (west, south, east, north)
CALIFORNIA_BBOX = "-124.5,32.5,-114.0,42.0"

# Default sensor: VIIRS NOAA-20 NRT (good resolution, actively maintained)
DEFAULT_SOURCE = "VIIRS_NOAA20_NRT"

BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

def get_map_key() -> str:
    """Return the FIRMS MAP_KEY from the environment. Raises if missing."""
    key = os.environ.get("FIRMS_MAP_KEY")
    if not key:
        raise RuntimeError(
            "FIRMS_MAP_KEY environment variable is not set."
            "Get a free key at https://firms.modaps.eosdis.nasa.gov/api/map_key/ "
            "and export it before running."
        )
    return key

def build_url(
        map_key: str,
        source: str = DEFAULT_SOURCE,
        bbox: str = CALIFORNIA_BBOX,
        day_range: int = 1,
        date: Optional[str] = None,
) -> str:
    """Build the FIRMS Area API URL."""
    if not 1 <= day_range <= 5:
        raise ValueError("day_range must be between 1 and 5")
    url = f"{BASE_URL}/{map_key}/{source}/{bbox}/{day_range}"
    if date:
        url = f"{url}/{date}"
    return url

def fetch_detections(
        source: str = DEFAULT_SOURCE,
        bbox: str = CALIFORNIA_BBOX,
        day_range: int = 1,
        date: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch detections from the FIRMS API and return a DataFrame.

    Raises on HTTP errors or non-CSV responses (e.g. invalid key).\
    """
    map_key = get_map_key()
    url = build_url(map_key, source, bbox, day_range, date)

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    text = response.text.strip()
    if not text or text.lower().startswith("<!doctype") or "invalid" in text.lower():
        raise RuntimeError(f"Unexpected response from FIRMS API: {text[:200]}")

    # Parse CSV
    df = pd.read_csv(StringIO(text))
    return df

def save_raw(df: pd.DataFrame, output_dir: str = "data/raw") -> Path:
    """Save the raw DataFrame to a timestamped CSV in the raw folder.

    Returns the path of the saved file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"firms_california_{timestamp}.csv"
    path = Path(output_dir) / filename
    df.to_csv(path, index=False)
    return path

def ingest(
        source: str = DEFAULT_SOURCE,
        bbox: str = CALIFORNIA_BBOX,
        day_range: int = 1,
        date: Optional[str] = None,
        output_dir: str = "data/raw",
) -> Path:
    """Full ingest: fetch from API and save raw CSV. Returns the saved path."""
    df = fetch_detections(source, bbox, day_range, date)
    path = save_raw(df, output_dir)
    print(f"Saved {len(df)} detections to {path}")
    return path

def ingest_last_n_days(n_days: int = 30, source: str = DEFAULT_SOURCE) -> None:
    """Pull the last n_days in 5-day chunks and save each as a raw CSV."""
    end = datetime.utcnow().date()
    start = end - timedelta(days=n_days)

    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        day_range = min(5, (end - current).days + 1)
        print(f"Fetching {date_str} for {day_range} days...")
        ingest(source=source, day_range=day_range, date=date_str)
        current += timedelta(days=day_range)

if __name__ == "__main__":
    ingest_last_n_days()