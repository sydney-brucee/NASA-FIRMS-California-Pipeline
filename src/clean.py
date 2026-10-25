"""Cleaning and validation for NASA FIRMS California wildfire detections.

Takes raw CSVs from data/raw/ and produces a cleaned DataFrame suitable for loading into a database.
"""

import pandas as pd
from pathlib import Path
from typing import List

REQUIRED_COLUMNS = [
    "latitude",
    "longitude",
    "bright_ti4",
    "confidence",
    "acq_date",
    "acq_time",
    "satellite",
    "frp",
]

def load_raw_files(raw_dir: str = "data/raw") -> pd.DataFrame:
    """Load and concatenate all raw CSVs in the raw directory."""
    paths = sorted(Path(raw_dir).glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    frames = [pd.read_csv(p) for p in paths]
    return pd.concat(frames, ignore_index=True)

def validate_columns(df: pd.DataFrame) -> None:
    """Raise if required columns are missing."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

def clean_detections(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate a raw FIRMS DataFrame.

    - Ensures required columns exist
    - Converts types
    - Drops rows with invalid coordinates or missing key fields
    - Adds a simple intensity bucket
    """

    validate_columns(df)
    out = df.copy()

    # Type conversions
    out["latitude"] = pd.to_numeric(out["latitude"], errors="coerce")
    out["longitude"] = pd.to_numeric(out["longitude"], errors="coerce")
    out["bright_ti4"] = pd.to_numeric(out["bright_ti4"], errors="coerce")
    out["frp"] = pd.to_numeric(out["frp"], errors="coerce")
    out["acq_date"] = pd.to_datetime(out["acq_date"], errors="coerce")

    # Dropping rows with critical missing values
    out = out.dropna(subset=["latitude", "longitude", "acq_date", "frp"])

    # Drop points clearly in Nevada
    out = out[
        (out["latitude"].between(32.5, 42.0))
        & (out["longitude"] >= -124.5)
        & (out["longitude"] <= -114.5)
        & ~(
            (out["latitude"] >= 38.5) & (out["longitude"] > -120.1)
        )
        & ~(
            (out["latitude"] >= 35.0) & (out["latitude"] < 38.5) & (out["longitude"] > -117.5)
        )
    ]

    # Simple intensity bucket based on FRP
    out["intensity"] = pd.cut(
        out["frp"],
        bins=[-1, 10, 50, 200, float("inf")],
        labels=["low", "moderate", "high", "extreme"],
    )

    # Keep a stable column order
    keep = REQUIRED_COLUMNS + ["intensity"]
    return out[keep].reset_index(drop=True)

def clean_from_raw(raw_dir: str = "data/raw") -> pd.DataFrame:
    """Convenience: load all raw files and return a cleaned DataFrame."""
    raw = load_raw_files(raw_dir)
    return clean_detections(raw)