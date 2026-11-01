# Source log: Project A data files

Raw files are not committed to GitHub. This log is.

| File | Publisher | Used for | Access / date | Notes |
|---|---|---|---|---|
| ghs-2025-household-v1.dta (inside ghs-2025-v1.zip) | Stats SA via DataFirst (UCT) | Households not paying for electricity (eng_pay), province (prov), household weight (house_wgt) | Downloaded by you; add date and DataFirst terms | 20,095 households; weights sum to 20,114,196, matching the published total |
| ies-2022-2023-total-v1.2.dta (inside ies-2022-2023-total-v1_2.zip) | Stats SA via DataFirst | Household income (COICOP types 3 and 4) and electricity spending (COICOP 4510100), annual | Downloaded by you; add date and DataFirst terms | One row per household per item; 19,940 households; weights sum to 21.28 million |
| ies-2022-2023-coicop-codelist.xlsx | Stats SA via DataFirst | Meaning of COICOP codes (4510100 electricity, 4510200 free electricity, 4510300 combined bill) | Downloaded by you | |
| ies-2022-2023-person-v1.2.dta | Stats SA via DataFirst | Not used yet. Has person weights and poverty-line flags (POOR1 to POOR3), no income amounts | Downloaded by you | Possible extension: a poverty-line measure of "can't pay" |
| P9115 Time series 2006-2023 by province.xlsx | Stats SA (Non-financial census of municipalities) | Indigent households identified, free basic electricity households, by province, 2023 | Downloaded by you | 2023 values carry an asterisk; check its meaning in the release |
| ghs-2025-statistical-release.pdf (P0318) | Stats SA | Household totals by province for reconciliation; meter types; 90.6% mains access | Uploaded by you | Report, not microdata |
| 2026 Budget Review (full) | National Treasury | Municipal debt relief programme: R85.2bn owed to Eskom in December 2025 by 71 participants; 15 consistently met conditions | Uploaded by you | Figure 6.1 shows historical overdue municipal debt owed to Eskom |

## Still to collect
- NERSA MYPD6 reasons for decision: allowable revenue (R384.61bn for 2025/26 from the 30 Jan 2025 media statement), forecast sales volumes (needed to replace the 192,710 GWh placeholder), and treatment of arrears and bad debt.
- Eskom FY2026 results and the ministerial replies NW4902 and NW5129 on the Parliamentary Monitoring Group site, to confirm the debt and non-recognised revenue figures.

## Assumptions to verify
- IES province = first digit of the household identifier (UQNO). Provincial household shares are within about 1 point of the GHS shares, but confirm with the IES geography file or published provincial IES tables.
- IES amounts are annual (divided by 12 in the config).
- The GHS and IES are from different years (2025 and 2022/23); tariffs have risen since the IES.
