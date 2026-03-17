# scripts/fetch_data.py
# ─────────────────────────────────────────────
# Step 1 of the pipeline: fetch raw data from
# data.gouv.fr and save to data/raw/
# ─────────────────────────────────────────────

import requests
import pandas as pd
from pathlib import Path
from config import SOURCES, RAW_DIR


def fetch_source(name: str, source: dict) -> pd.DataFrame:
    """
    Download a CSV from data.gouv.fr and save it as-is to data/raw/.
    Returns the DataFrame for immediate inspection.

    Why save raw first?
    → Reproducibility: if the URL changes or goes down, you still have the data.
    → Auditability: raw ≠ processed, always traceable.
    """
    print(f" Fetching: {name} — {source['description']}")

    response = requests.get(source["url"], timeout=30)
    response.raise_for_status()

    output_path = RAW_DIR / source["filename"]
    output_path.write_bytes(response.content)
    print(f" Saved to {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")

    # Read back from disk to return consistent DataFrame
    df = pd.read_csv(output_path, sep=source["sep"], low_memory=False)
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    return df


def fetch_all() -> dict[str, pd.DataFrame]:
    """Fetch all configured sources and return them as a dict of DataFrames."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    results = {}
    for name, source in SOURCES.items():
        try:
            results[name] = fetch_source(name, source)
        except requests.HTTPError as e:
            print(f"HTTP error for {name}: {e}")
        except Exception as e:
            print(f"Unexpected error for {name}: {e}")

    return results


if __name__ == "__main__":
    print("=" * 50)
    print("Santé Occitanie — Data Fetch")
    print("=" * 50)

    dataframes = fetch_all()

    print("\nColumn preview:")
    for name, df in dataframes.items():
        print(f"\n[{name}]")
        print(df.dtypes)
        print(df.head(3))
