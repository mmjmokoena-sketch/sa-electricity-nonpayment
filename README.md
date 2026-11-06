See [FINDINGS.md](projects/a_who_pays/paper/FINDINGS.md) for a one-page summary.
# SA electricity non-payment

Personal research repository on electricity non-payment, tariffs and affordability in South
Africa. Three linked projects: A (who pays), B (tariff audit), C (tipping point).

## Quick start

```
conda env create -f environment.yml
conda activate sa-electricity
make demo        # runs everything on FAKE demo data to check the setup
```

When the real data is downloaded, set `data_mode: raw` in `config/assumptions.yaml`, update
`paths` and `column_map`, then run `make all`.

## Data

Raw survey files are not stored here (licences usually forbid redistribution). See
`data/raw/SOURCES.md` for where to get each file.




## Status

Project A: in completed.
