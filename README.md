# Santé Occitanie — Power BI Portfolio Project

> Analyse de la pression hospitalière en Occitanie : capacité, réanimations et mortalité (2020–2024)

---

## Project goal

Build an end-to-end data pipeline and Power BI dashboard that answers:

> *Is Occitanie's hospital system under stress — where, when, and how severely?*

**Data source:** [data.gouv.fr](https://www.data.gouv.fr) — no API key required  
**Stack:** Python → CSV → Power BI Desktop  
**Scope:** 13 Occitanie départements, daily granularity

---

## Project structure

```
sante-occitanie/
│
├── data/
│   ├── raw/              # API responses (never edit manually)
│   └── processed/        # Power BI-ready CSVs
│
├── scripts/
│   ├── config.py         # Constants: URLs, dept codes, wave periods
│   ├── fetch_data.py     # Step 1: download raw data
│   ├── transform.py      # Step 2: clean, filter, export tables
│   └── run_pipeline.py   # One-command runner
│
├── powerbi/
│   └── sante_occitanie.pbix   # (to be created in Power BI Desktop)
│
├── docs/
│   └── schema.md         # Table schema + DAX measures
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting started

### 1. Install dependencies

```bash
uv sync
```

### 2. Run the full pipeline

```bash
uv run -m scripts.run_pipeline
```

This will:
- Download raw data from data.gouv.fr into `data/raw/`
- Clean, filter to Occitanie, and enrich the data
- Export 4 Power BI-ready tables into `data/processed/`

### 3. Import into Power BI Desktop

1. Open Power BI Desktop
2. **Get data → Text/CSV**
3. Import all 4 files from `data/processed/`:
   - `fact_hospital.csv`
   - `dim_dept.csv`
   - `dim_date.csv`
   - `dim_waves.csv`
4. Go to **Model view** and set relationships:
   - `fact_hospital[date]` → `dim_date[date]`
   - `fact_hospital[dept_id]` → `dim_dept[dept_id]`

---

## Dashboard structure (suggested)

| Page | Title | Key visuals |
|---|---|---|
| 1 | Vue d'ensemble | KPI cards, line chart, map by département |
| 2 | Comparaison inter-départementale | Bar chart, scatter (population vs. ICU peak) |
| 3 | Analyse des vagues | Timeline, wave comparisons, Occitanie vs. national |

---

##  Data model

See [docs/schema.md](docs/schema.md) for full column descriptions and DAX measures.

---

##  Data sources

| Dataset | Source | Frequency |
|---|---|---|
| Données hospitalières COVID | data.gouv.fr / Santé Publique France | Daily |
| Passages aux urgences | data.gouv.fr / DREES | Weekly |

---

##  Ideas to extend this project

- Add **INSEE demographics** (age pyramid per département) to contextualize mortality
- Pull **SOS Médecins** call volume as a leading indicator
- Add a **forecast page** using Python visuals in Power BI
- Publish to **Power BI Service** for a shareable URL


