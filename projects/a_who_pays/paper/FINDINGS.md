# Who pays for electricity in South Africa, and who can't?

**Project A: findings brief** | Author: Mokgele | November 2026 | Status: preliminary

## Question
How many South African households do not pay for electricity, how many of them could afford a bill, and what would that mean for Eskom's revenue and for the price other customers pay?

## Data and method
- **GHS 2025** household file (Stats SA): who says they do not pay. Weighted totals match the published 20.11 million households.
- **IES 2022/23** (Stats SA): household income and electricity spending. A household is "unable" when its bill is at or above 10% of income (8% and 12% also tested).
- **NFCM 2023** (Stats SA): registered indigent households by province.
- The two surveys cannot be linked household by household, so I give a **range** under stated assumptions about who the non-payers are, not a single guess. All code, tests and notebooks are in this repository and rebuild from the raw files.

## Main findings (all estimates)
| Finding | Result |
|---|---|
| Households saying they do not pay | **about 2.67 million**, 14.7% of those answering yes or no |
| Households with a bill at or above 10% of income | **18.4%** (about 3.0 million of 16.4 million); 24.3% at 8%, 14.3% at 12%. Stable across checks (17.8% to 20.0%) |
| Where it is highest | KwaZulu-Natal by share (22.2%); Gauteng by number (about 723,000) |
| Non-payers who could afford a bill (10% line) | **1.35 to 2.63 million**, middle case 2.17 million. With only own-meter non-payers (2.14 million): 0.98 to 2.13 million |
| Indigent coverage (R4,500 a month cut-off) | 2.76 million registered against 6.04 million households under the cut-off, **46%**; from 18% in Mpumalanga to about 100% in KwaZulu-Natal |
| Extra revenue if able-to-pay non-payers paid | **about R5 to R11 billion a year** (1.4% to 2.9% of Eskom's R384.61 billion allowable revenue), about half going to Eskom directly |
| Effect on the price other customers pay | a stylised fall of about 2% to 4%, and not a change in the legal tariff |
| Real price at which half of households with a bill reach 10% of income | about **2.6 times** the 2022/23 level; about 1.3 times today (rough), so roughly 10 years at 7% real growth |

## What this does and does not show
- Collecting more would **not automatically lower tariffs**. NERSA sets tariffs from allowable revenue, and the benefit shows up as a smaller Eskom shortfall and less pressure for future increases.
- Being above the 10% line is **not the same as defaulting**. How many households actually stop paying is the question for Project C.
- Most of Eskom's non-payment problem is **municipal**: municipalities owe Eskom about R120 billion (reported, to be verified), far more than household recovery could close.

## Limits and known issues
- Survey years differ (income 2022/23, payment 2025), and tariffs have risen since. Bills are scaled using tariff increases; the central factor should be about 1.35, not 1.34 (about 1% effect).
- The IES province is inferred from the household ID. Totals and plausibility checks support it.
- "No" to paying may include electricity included in rent or use covered by free basic units, and prepaid households answering "No" are unexplained.
- Indigent income cut-offs are my assumption; municipalities set their own.
- The sales volume used for cents-per-kWh figures is a placeholder, so I do not quote them.
- Some reported figures (municipal debt totals, revenue not recognised) are not yet verified against primary sources.

## Reproduce
Clone the repository, add the Stats SA files to `data/raw/statssa/`, then run `prepare_inputs`, `run_all` and `pytest` (see `START_HERE.md`). Raw survey data is not included because of licence terms.

*Code scaffolding was written with AI assistance. Data collection, source checks, interpretation and conclusions are the author's own.*
