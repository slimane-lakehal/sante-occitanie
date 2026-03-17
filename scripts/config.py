# scripts/config.py
# ─────────────────────────────────────────────
# Shared constants used across the pipeline
# ─────────────────────────────────────────────

from pathlib import Path

# ── Paths ──────────────────────────────────────
ROOT_DIR       = Path(__file__).resolve().parent.parent
RAW_DIR        = ROOT_DIR / "data" / "raw"
PROCESSED_DIR  = ROOT_DIR / "data" / "processed"

# ── Occitanie départements (INSEE codes) ───────
OCCITANIE_DEPTS = [
    "09",  # Ariège
    "11",  # Aude
    "12",  # Aveyron
    "30",  # Gard
    "31",  # Haute-Garonne
    "32",  # Gers
    "34",  # Hérault
    "46",  # Lot
    "48",  # Lozère
    "65",  # Hautes-Pyrénées
    "66",  # Pyrénées-Orientales
    "81",  # Tarn
    "82",  # Tarn-et-Garonne
]

DEPT_NAMES = {
    "09": "Ariège",
    "11": "Aude",
    "12": "Aveyron",
    "30": "Gard",
    "31": "Haute-Garonne",
    "32": "Gers",
    "34": "Hérault",
    "46": "Lot",
    "48": "Lozère",
    "65": "Hautes-Pyrénées",
    "66": "Pyrénées-Orientales",
    "81": "Tarn",
    "82": "Tarn-et-Garonne",
}

# Population estimée par département (INSEE 2023, pour calculs per capita)
DEPT_POPULATION = {
    "09": 153_153,
    "11": 378_760,
    "12": 279_595,
    "30": 748_432,
    "31": 1_425_612,
    "32": 191_283,
    "34": 1_175_623,
    "46": 174_526,
    "48": 76_601,
    "65": 226_672,
    "66": 479_295,
    "81": 387_890,
    "82": 260_928,
}

# ── Data sources (data.gouv.fr — no auth needed) ───
SOURCES = {
    "hospital_covid": {
        "url": "https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7",
        "filename": "hospital_covid_raw.csv",
        "sep": ";",
        "description": "Données hospitalières COVID par département (quotidien)",
    },
    "urgences": {
        "url": "https://www.data.gouv.fr/fr/datasets/r/eceb9fb4-3ebc-4da3-828d-f5939712600a",
        "filename": "urgences_raw.csv",
        "sep": ";",
        "description": "Passages aux urgences par région (hebdomadaire)",
    },
}

# ── COVID wave periods (for annotations in Power BI) ───
COVID_WAVES = [
    {"wave": 1, "label": "Vague 1", "start": "2020-03-17", "end": "2020-05-11"},
    {"wave": 2, "label": "Vague 2", "start": "2020-10-01", "end": "2020-12-15"},
    {"wave": 3, "label": "Vague 3", "start": "2021-03-01", "end": "2021-05-31"},
    {"wave": 4, "label": "Vague 4 (Delta)", "start": "2021-07-01", "end": "2021-09-30"},
    {"wave": 5, "label": "Vague 5 (Omicron)", "start": "2021-12-01", "end": "2022-02-28"},
]
