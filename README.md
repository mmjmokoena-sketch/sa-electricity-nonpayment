# SA electricity non-payment

Personal research repository on electricity non-payment, tariffs and affordability in South
Africa. Three linked projects: **A (who pays)**, B (tariff audit, planned) and C (tipping point, planned).

**Start here:** [FINDINGS.md](projects/a_who_pays/paper/FINDINGS.md) is a one-page summary of Project A.

## Status

Project A is complete (v1.0). Results are **preliminary**: some reported figures are not yet verified
against primary sources, and the known issues are listed in the findings brief.

## Headline results (estimates)

- About **2.67 million households** say they do not pay for electricity (14.7% of those answering yes or no).
- **18.4%** of households with an electricity bill spend 10% or more of their income on it
  (17.8% to 20.0% across robustness checks).
- Between **1.35 and 2.63 million** of the non-paying households could afford a bill. If they paid, that
  would add roughly **R5 to R11 billion a year**, about half of it to Eskom directly.

## Reproduce

Requires [Miniconda](https://docs.conda.io/en/latest/miniconda.html) and the Stats SA files described under Data.

```
conda env create -f environment.yml
conda activate sa-electricity
python -m pytest -q                              # 23 tests
python -m src.a_who_pays.run_all --mode synthetic    # fake demo data, checks the setup
```

With the real files in `data/raw/statssa/`:

```
python -m src.common.prepare_inputs
python -m src.a_who_pays.run_all
python -m src.a_who_pays.robustness
```

Never publish results made from the `--mode synthetic` demo data.

## Data

Raw survey files are **not included** (licence terms). Download them and place them in `data/raw/statssa/`:

- General Household Survey 2025, household file (Stats SA via DataFirst)
- Income and Expenditure Survey 2022/23, total file v1.2 (Stats SA via DataFirst)
- Non-financial census of municipalities, time series 2006 to 2023 (Stats SA)

See `data/raw/SOURCES.md` for sources, dates and access notes.

## What is in the repository

| Folder | Contents |
|---|---|
| `src/` | code: data preparation, affordability, split, revenue and price-multiplier analysis |
| `projects/a_who_pays/notebooks/` | seven notebooks with written answers |
| `projects/a_who_pays/outputs/` | aggregated tables and charts (no household-level data) |
| `tests/` | automated checks |
| `config/` | all settings and assumptions in one file |

## Notes

- Code scaffolding was written with AI assistance. Data collection, source checks, interpretation and
  conclusions are my own.
- Licences: code under MIT, text and aggregated tables under CC BY 4.0 (see `LICENSE` and `LICENSE-DATA.md`).