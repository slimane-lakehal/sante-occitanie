# Data Schema — Santé Occitanie

## Overview

Star schema with 1 fact table and 3 dimension tables.
All files are in `data/processed/` after running the pipeline.

---

## fact_hospital.csv

> Grain: 1 row per département per day

| Column | Type | Description |
|---|---|---|
| `date` | date | Calendar day |
| `dept_id` | string | INSEE département code (ex: `"34"`) |
| `hosp_occupied` | int | Hospitalisations en cours |
| `icu_occupied` | int | Réanimations (ICU) en cours |
| `deaths_cumul` | int | Décès cumulés depuis le début |
| `deaths_daily` | float | Décès du jour (diff du cumulé) |
| `returned_home_cumul` | int | Retours à domicile cumulés |
| `hosp_per_100k` | float | Hospitalisations pour 100 000 hab. |
| `icu_per_100k` | float | Réanimations pour 100 000 hab. |
| `wave_label` | string | Ex: `"Vague 3"`, `"Hors vague"` |

**Relationships:**
- `date` → `dim_date.date`
- `dept_id` → `dim_dept.dept_id`

---

## dim_dept.csv

> Grain: 1 row per département (13 total for Occitanie)

| Column | Type | Description |
|---|---|---|
| `dept_id` | string | INSEE code (ex: `"34"`) |
| `dept_name` | string | Ex: `"Hérault"` |
| `region` | string | Always `"Occitanie"` |
| `population` | int | Population INSEE 2023 |

---

## dim_date.csv

> Grain: 1 row per calendar day

| Column | Type | Description |
|---|---|---|
| `date` | date | Primary key |
| `year` | int | Ex: `2021` |
| `month_num` | int | 1–12 |
| `month_label` | string | Ex: `"March"` |
| `month_short` | string | Ex: `"Mar"` |
| `week_num` | int | ISO week number |
| `quarter` | int | 1–4 |
| `quarter_label` | string | Ex: `"T2"` |
| `weekday_num` | int | 0=Monday, 6=Sunday |
| `weekday_label` | string | Ex: `"Monday"` |
| `is_weekend` | bool | True for Sat/Sun |
| `year_month` | string | Ex: `"2021-03"` |
| `wave_label` | string | Same as fact_hospital |

---

## dim_waves.csv

> Grain: 1 row per COVID wave

| Column | Type | Description |
|---|---|---|
| `wave` | int | Wave number (1–5) |
| `label` | string | Ex: `"Vague 3"` |
| `start` | date | Wave start date |
| `end` | date | Wave end date |
| `duration_days` | int | Length of wave in days |

---

## Power BI Relationships

```
fact_hospital[date]    → dim_date[date]      (Many to One)
fact_hospital[dept_id] → dim_dept[dept_id]   (Many to One)
```

> `dim_waves` is not directly related — use it as a reference table
> for custom annotations or slicer values.

---

## Suggested DAX Measures

```dax
-- Total hospitalisations (context-aware)
Total Hosp = SUM(fact_hospital[hosp_occupied])

-- Peak ICU day
Peak ICU = MAX(fact_hospital[icu_occupied])

-- Taux d'occupation moyen ICU (per 100k)
Avg ICU per 100k = AVERAGE(fact_hospital[icu_per_100k])

-- Décès totaux (last value of cumul, not sum!)
Total Deaths =
    CALCULATE(
        MAX(fact_hospital[deaths_cumul]),
        ALLEXCEPT(fact_hospital, fact_hospital[dept_id])
    )

-- Variation hebdomadaire hospitalisations
WoW Hosp % =
VAR current = [Total Hosp]
VAR previous = CALCULATE([Total Hosp], DATEADD(dim_date[date], -7, DAY))
RETURN DIVIDE(current - previous, previous)
```
