# scripts/transform.py
# ─────────────────────────────────────────────
# Step 2 of the pipeline: clean, filter, enrich
# and export Power BI-ready tables to data/processed/
# ─────────────────────────────────────────────

import pandas as pd
from pathlib import Path
from config import (
    RAW_DIR,
    PROCESSED_DIR,
    OCCITANIE_DEPTS,
    DEPT_NAMES,
    DEPT_POPULATION,
    COVID_WAVES,
)


# ── Helpers ────────────────────────────────────────────────────────────────

def save(df: pd.DataFrame, filename: str) -> None:
    """Save a processed DataFrame to data/processed/ as CSV."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")  # utf-8-sig for Excel compat
    print(f"Saved {filename} — {df.shape[0]:,} rows × {df.shape[1]} columns")


def flag_wave(date: pd.Timestamp) -> str:
    """Return the wave label for a given date, or 'Hors vague'."""
    for w in COVID_WAVES:
        if pd.Timestamp(w["start"]) <= date <= pd.Timestamp(w["end"]):
            return w["label"]
    return "Hors vague"


# ── Table builders ─────────────────────────────────────────────────────────

def build_fact_hospital(raw_path: Path) -> pd.DataFrame:
    """
    Build the main fact table from the COVID hospital dataset.

    Source columns (data.gouv.fr):
        dep, sexe, jour, hosp, rea, rad, dc

    hosp = hospitalisations en cours
    rea  = réanimations (ICU) en cours
    rad  = retours à domicile cumulés
    dc   = décès cumulés
    sexe = 0 (total), 1 (homme), 2 (femme)
    """
    print("Building fact_hospital...")
    df = pd.read_csv(raw_path, sep=";", low_memory=False)

    # Keep only total rows (sexe == 0 avoids double-counting)
    df = df[df["sexe"] == 0].copy()

    # Filter to Occitanie
    df = df[df["dep"].astype(str).str.zfill(2).isin(OCCITANIE_DEPTS)].copy()
    df["dep"] = df["dep"].astype(str).str.zfill(2)

    # Parse dates
    df["jour"] = pd.to_datetime(df["jour"])

    # Rename for clarity
    df = df.rename(columns={
        "dep":  "dept_id",
        "jour": "date",
        "hosp": "hosp_occupied",
        "rea":  "icu_occupied",
        "rad":  "returned_home_cumul",
        "dc":   "deaths_cumul",
    })

    # Derived metrics
    df["deaths_daily"] = (
        df.sort_values("date")
          .groupby("dept_id")["deaths_cumul"]
          .diff()
          .clip(lower=0)  # removes negative artefacts from data corrections
    )

    df["hosp_per_100k"] = (
        df["dept_id"].map(DEPT_POPULATION)
        .pipe(lambda pop: df["hosp_occupied"] / pop * 100_000)
        .round(2)
    )

    df["icu_per_100k"] = (
        df["dept_id"].map(DEPT_POPULATION)
        .pipe(lambda pop: df["icu_occupied"] / pop * 100_000)
        .round(2)
    )

    # Wave flag (useful for filtering/coloring in Power BI)
    df["wave_label"] = df["date"].apply(flag_wave)

    # Clean up columns
    df = df[[
        "date", "dept_id",
        "hosp_occupied", "icu_occupied",
        "deaths_cumul", "deaths_daily",
        "returned_home_cumul",
        "hosp_per_100k", "icu_per_100k",
        "wave_label",
    ]].sort_values(["dept_id", "date"])

    return df


def build_dim_dept() -> pd.DataFrame:
    """
    Dimension table: one row per département.
    Enriched with names and population.
    """
    print("Building dim_dept...")
    records = [
        {
            "dept_id":    dept_id,
            "dept_name":  DEPT_NAMES[dept_id],
            "region":     "Occitanie",
            "population": DEPT_POPULATION[dept_id],
        }
        for dept_id in OCCITANIE_DEPTS
    ]
    return pd.DataFrame(records)


def build_dim_date(start: str, end: str) -> pd.DataFrame:
    """
    Dimension table: one row per calendar day.
    Pre-computed columns for Power BI time intelligence.
    """
    print(" Building dim_date...")
    dates = pd.date_range(start=start, end=end, freq="D")
    df = pd.DataFrame({"date": dates})

    df["year"]          = df["date"].dt.year
    df["month_num"]     = df["date"].dt.month
    df["month_label"]   = df["date"].dt.strftime("%B")          # "janvier", etc. (locale-dependent)
    df["month_short"]   = df["date"].dt.strftime("%b")
    df["week_num"]      = df["date"].dt.isocalendar().week.astype(int)
    df["quarter"]       = df["date"].dt.quarter
    df["quarter_label"] = "T" + df["quarter"].astype(str)
    df["weekday_num"]   = df["date"].dt.weekday                 # 0 = Monday
    df["weekday_label"] = df["date"].dt.strftime("%A")
    df["is_weekend"]    = df["weekday_num"].isin([5, 6])
    df["year_month"]    = df["date"].dt.to_period("M").astype(str)  # "2025-03"
    df["wave_label"]    = df["date"].apply(flag_wave)

    return df


def build_dim_waves() -> pd.DataFrame:
    """
    Dimension table: one row per COVID wave.
    Used for reference/annotation in Power BI visuals.
    """
    print("Building dim_waves...")
    df = pd.DataFrame(COVID_WAVES)
    df["start"] = pd.to_datetime(df["start"])
    df["end"]   = pd.to_datetime(df["end"])
    df["duration_days"] = (df["end"] - df["start"]).dt.days
    return df


# ── Main ───────────────────────────────────────────────────────────────────

def run():
    print("=" * 50)
    print(" Santé Occitanie — Transform")
    print("=" * 50)

    raw_hospital = RAW_DIR / "hospital_covid_raw.csv"

    if not raw_hospital.exists():
        print(" Raw data not found. Run fetch_data.py first.")
        return

    fact_hospital = build_fact_hospital(raw_hospital)
    dim_dept      = build_dim_dept()
    dim_date      = build_dim_date(
        start=str(fact_hospital["date"].min().date()),
        end=str(fact_hospital["date"].max().date()),
    )
    dim_waves = build_dim_waves()

    print("\nSaving processed tables...")
    save(fact_hospital, "fact_hospital.csv")
    save(dim_dept,      "dim_dept.csv")
    save(dim_date,      "dim_date.csv")
    save(dim_waves,     "dim_waves.csv")

    print("\nAll tables ready — import data/processed/ into Power BI.")
    print(f"fact_hospital: {fact_hospital['date'].min().date()} → {fact_hospital['date'].max().date()}")
    print(f"Départements:  {fact_hospital['dept_id'].nunique()} / 13 Occitanie")


if __name__ == "__main__":
    run()
