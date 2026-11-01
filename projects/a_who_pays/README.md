# Project A: definitions (frozen before interpreting results)

## Data
- GHS 2025 household file (DataFirst): weights house_wgt, province prov, payment eng_pay.
- IES 2022/23 item file v1.2 (DataFirst): income and electricity spending, annual rand.
- NFCM time series 2006-2023 (Stats SA): indigent and free basic electricity households, 2023*.

## Definitions
- Non-payer: household answering "No" to paying for electricity (eng_pay = 2), among households answering Yes or No.
- Income: annual cash plus in-kind income (IES types 3 and 4), divided by 12 for monthly.
- Electricity bill: COICOP 4510100 only. The combined water-and-electricity item 4510300 is excluded.
- Affordability line: bill at least 8%, 10% or 12% of income. Headline 10% (a convention).
- Able to pay: bill share below the line.
- Who the non-payers are: unknown, so tested as a random draw from the poorest 30%, 50%, 70% and 100% of paying households, plus the two extremes.
- Prices: IES bills (2022/23) scaled to 2025/26 using tariff increases. Factors 1.271 (low), 1.34 (central), 1.508 (high).
- Collection: 50%, 70% and 100% of able-to-pay non-payers.
- Tariff block: allowable revenue R384.61bn (NERSA, 30 Jan 2025). Unpaid share of revenue 4.5% (R15.8bn not recognised, FY2026).
- Indigent comparison: income cut-offs R3,000, R4,500 and R6,000 a month.

## Known assumptions and limits
- IES province is the first digit of the household ID (to verify).
- The IES is 2022/23 and the GHS is 2025; tariffs rose in between.
- Sales volume of 192,710 GWh is a placeholder until confirmed in NERSA's reasons for decision.
- Real price multiplier today (1.28) is a rough estimate.
- Prepaid and neighbour-supplied households answering "No" need explaining.