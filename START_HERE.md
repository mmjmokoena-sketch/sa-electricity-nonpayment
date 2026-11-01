# Project A: start here

This folder is the complete, tested project. Nothing else needs to be added except your data files.

## 1. Move it somewhere sensible
Copy this folder out of Downloads, for example to C:\Users\mmjmo\Projects\sa-electricity-nonpayment

## 2. Open PowerShell in the folder and set up the environment (once)
    conda env create -f environment.yml
    conda activate sa-electricity

## 3. Check it works on FAKE demo data
    python -m pytest -q                                   (expect 20 passed)
    python -m src.a_who_pays.run_all --mode synthetic     (prints a SYNTHETIC warning)

## 4. Add your real data
Put your three Stats SA files in data/raw/statssa/ (see PUT_YOUR_FILES_HERE.txt), then:
    python -m src.common.prepare_inputs
    python -m src.a_who_pays.run_all

## 5. Where things are
- config/assumptions.yaml     every setting and assumption (change things here)
- src/                        the code
- projects/a_who_pays/notebooks/   seven notebooks to run and answer
- data/raw/SOURCES.md         source log for the data files
- docs/ and dashboards/       the website and dashboard
- Project_A_Complete_Guide.docx    the written guide (separate file)

Never commit anything from data/raw or data/interim to GitHub, and never publish results made from demo data.
