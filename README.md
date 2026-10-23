# California Wildfire Detection Data Pipeline

A local data engineering pipeline that ingests wildfire detections from the NASA FIRMS API for California. Stage 1 pulls the most recent day of data and saves raw CSVs. Later stages will add cleaning, storage, and a dashboard.

## Current stage

**Stage 2: Cleaning and validation =**

- Loads all raw CSVs from `data/raw`
- Validates required columns and converts types
- Drops rows with missing critical fields or coordinates outside California
- Adds a simple intensity bucket based on FRP
- Includes unit tests

Later stages will add cleaning, a local database, analytics views, and a Streamlit dashboard.

## Setup

1. Clone the repository and create a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Activate it:

   - Windows (PowerShell): `.venv\Scripts\activate`
   - macOS / Linux: `source .venv/bin/activate`

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Get a free NASA FIRMS MAP_KEY:
   - Go to https://firms.modaps.eosdis.nasa.gov/api/map_key/
   - Register and copy your key

4. Create a `.env` file in the project root (recommended):
   FIRMS_MAP_KEY=your_actual_key_here
   Do not commit the `.env` file.

   **Alternative:** set the key in the terminal for the current session:
   ### Windows PowerShell
   $env:FIRMS_MAP_KEY = "your_key_here"

   ### macOS / Linux
   export FIRMS_MAP_KEY="your_key_here"

## Run the Ingest

From the project root:

```bash
python -m src.ingest
```

This fetches the last 30 days of VIIRS NOAA-20 detections for California (in 5-day chunks) and saves timestamped CSVs in `data/raw/`.

## Run the Cleaning

```bash
python -c "from src.clean import clean_from_raw; df = clean_from_raw(); print(df.head()); print(len(df))"
```

## Running Tests

```bash
python tests/ -v
```

## Project Structure

```
.
├── src/
│   └── ingest.py          # API client and raw save
|   └── clean.py           # Cleaning and validation
├── tests/
|   └── test_clean.py      # Unit tests for cleaning
├── data/
│   └── raw/               # Timestamped raw CSVs
├── requirements.txt
├── .env.example
├──.gitignore
└── README.md
```

## Next stages

- Stage 3: Load into SQLite
- Stage 4: SQL analytics views
- Stage 5: Streamlit dashboard
- Stage 6: Scheduling and final documentation
