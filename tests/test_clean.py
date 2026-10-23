"""Unit tests for src.clean."""

import pandas as pd
import pytest

from src.clean import clean_detections, validate_columns


@pytest.fixture
def raw_sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "latitude": [34.5, 36.0, 50.0, 35.0],
            "longitude": [-118.0, -120.0, -120.0, -130.0],
            "bright_ti4": [320.0, 350.0, 300.0, 310.0],
            "confidence": ["n", "h", "l", "n"],
            "acq_date": ["2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04"],
            "acq_time": [1200, 1300, 1400, 1500],
            "satellite": ["N", "N", "N", "N"],
            "frp": [5.0, 25.0, 80.0, 15.0],
        }
    )


def test_validate_columns_ok(raw_sample: pd.DataFrame) -> None:
    validate_columns(raw_sample)  # should not raise


def test_validate_columns_missing() -> None:
    df = pd.DataFrame({"latitude": [1.0]})
    with pytest.raises(ValueError):
        validate_columns(df)


def test_clean_detections_filters_bad_coords(raw_sample: pd.DataFrame) -> None:
    cleaned = clean_detections(raw_sample)
    # Row with lat=50 and row with lon=-130 should be dropped
    assert len(cleaned) == 2
    assert cleaned["latitude"].between(32.0, 42.5).all()
    assert cleaned["longitude"].between(-125.0, -114.0).all()


def test_clean_detections_adds_intensity(raw_sample: pd.DataFrame) -> None:
    cleaned = clean_detections(raw_sample)
    assert "intensity" in cleaned.columns
    assert set(cleaned["intensity"].dropna().unique()).issubset(
        {"low", "moderate", "high", "extreme"}
    )


def test_clean_detections_drops_missing_dates() -> None:
    df = pd.DataFrame(
        {
            "latitude": [34.5],
            "longitude": [-118.0],
            "bright_ti4": [320.0],
            "confidence": ["n"],
            "acq_date": [None],
            "acq_time": [1200],
            "satellite": ["N"],
            "frp": [10.0],
        }
    )
    cleaned = clean_detections(df)
    assert cleaned.empty
