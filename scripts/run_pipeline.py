# scripts/run_pipeline.py
# ─────────────────────────────────────────────
# One-command pipeline runner:
#   python scripts/run_pipeline.py
# ─────────────────────────────────────────────

import sys
import os

# Make sure scripts/ is in the path when running from root
sys.path.insert(0, os.path.dirname(__file__))

import fetch_data
import transform

if __name__ == "__main__":
    print(" Running full pipeline...\n")
    fetch_data.fetch_all()
    print()
    transform.run()
    print("\n Pipeline complete. Open Power BI and import data/processed/")
