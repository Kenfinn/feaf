# Automatic DCF Valuation Documentation (Task B2)

This document describes the architecture, the data source mapping, the comparison against the manual `2330` worksheet, the evaluation results for 10 random non-financial issuers across both exchanges (TWSE & TPEx), and technical notes for parallel development.

---

## 1. Purpose & Architecture

Before Task B2, only `2330` (TSMC) had a manual valuation input file (`valuation/inputs/2330.json`). As a result:
- Clause 20/11/22 announcements for issuers other than `2330` ended up held (`HELD`) with the reason `tanpa_valuasi` (no valuation).
- The **Valuation** tab on the stock page (`/saham/{kode}?tab=valuasi`) was empty for all issuers except `2330`.

The module [`app/valuasi_otomatis.py`](../app/valuasi_otomatis.py) and the CLI [`scripts/valuasi_otomatis.py`](../scripts/valuasi_otomatis.py) build the DCF input structure with **exactly the same schema** as `valuation/inputs/2330.json`, so that [`scripts/dcf.py`](../scripts/dcf.py) (`compute()`) and [`app/agent/recompute.py`](../app/agent/recompute.py) (`hitung_ulang()`) can be used directly without changing a single line in the DCF arithmetic engine.

### Storage Flow & Source Priority
1. **The manual file always wins**: `app/store.py::muat_valuasi(kode)` checks `valuation/inputs/{kode}.json` first. If it exists, the manual file is returned as is.
2. **Automatic cache without network on the pipeline path**: if there is no manual file, `store.muat_valuasi(kode)` calls `valuasi_otomatis.dari_cache_untuk_pipeline(kode)`, which only reads `DATA_DIR/valuasi_otomatis/{kode}.json` from disk (it never calls the internet so the pipeline stays deterministic and fast).
3. **Scheduled warm-up**: `_pemantau()` and the `POST /periksa` route in `app/main.py` call `valuasi_otomatis.panaskan(tarik.baca_watchlist())` before `hasil(segarkan=True)` with polite delays and a 12-hour cache TTL.
4. **Refresh on a new financial report**: the function `valuasi_otomatis.segarkan(kode)` is provided so that the clause 31 announcement monitor (publication of a new financial report) can immediately rebuild the valuation cache of the issuer concerned.

---

## 2. Field Mapping & Data Sources

All monetary values are stored in **million NTD** (FinMind values in NTD divided by $10^6$):

| Section | `2330.json` Field | Automatic Source | Formula / Rule |
|---|---|---|---|
| `market` | `price_per_share` | `pasar.harga(kode)["tutup"]` | Daily closing price from the TWSE OpenAPI (`STOCK_DAY_ALL`) / TPEx (`tpex_mainboard_quotes`) |
| `market` | `shares_issued_thousands` | `pasar.profil(kode)["lembar"]` | Outstanding ordinary shares divided by $1{,}000$; fallback `CapitalStock / 10 / 1000` (par value NT\$10) if the exchange profile is empty |
| `balance_sheet` | `cash_and_equivalents` | FinMind `TaiwanStockBalanceSheet` | `CashAndCashEquivalents / 1e6` at the end of the fiscal year (`{fiscal_year}-12-31`, or the latest quarter if not yet available) |
| `balance_sheet` | `short_term_investments` | FinMind `TaiwanStockBalanceSheet` | `(FinancialAssetsAtAmortizedCost + FinancialAssetsAtFairvalueThroughOtherComprehensiveIncome) / 1e6` |
| `balance_sheet` | `current_portion_lt_debt` | FinMind `TaiwanStockBalanceSheet` | `LongtermLiabilitiesCurrentPortion` / items whose `origin_name` contains `一年內到期` + `ShorttermBorrowings` (see the note in section 3) |
| `balance_sheet` | `long_term_debt` | FinMind `TaiwanStockBalanceSheet` | `(BondsPayable + LongtermBorrowings) / 1e6` |
| `cash_flow` | `cfo_by_year` | FinMind `TaiwanStockCashFlowsStatement` | `CashFlowsFromOperatingActivities / 1e6` for the last 3 full fiscal years (`-12-31`, because FinMind cash flows are cumulative YTD since the start of the year) |
| `cash_flow` | `capex_by_year` | FinMind `TaiwanStockCashFlowsStatement` | `abs(PropertyAndPlantAndEquipment) / 1e6` for the last 3 full fiscal years (`-12-31`) |
| `cash_flow` | `interest_expense_by_year` | FinMind `TaiwanStockCashFlowsStatement` | `abs(InterestExpense) / 1e6`, or falls back to `abs(PayTheInterest) / 1e6` if `InterestExpense` is absent (recorded in `sources` and `peringatan` (warnings)) |
| `tax` | `income_tax_expense`, `pretax_income` | FinMind `TaiwanStockFinancialStatements` | Sum of the 4 single quarters of the last fiscal year: `sum(TAX) / 1e6` and `sum(PreTaxIncome) / 1e6` |
| `wacc_inputs` | `risk_free_rate`, `equity_risk_premium` | Taiwan market constants (`2330.json`) | $r_f = 1.94\%$ (Taiwan 10Y government bond), $\text{ERP} = 5.01\%$ (Damodaran Taiwan) |
| `wacc_inputs` | `beta` | Yahoo Finance chart API (`2y`, `1wk`) | $\beta = \frac{\text{Cov}(r_s, r_m)}{\text{Var}(r_m)}$ between the weekly returns of `{kode}.TW`/`.TWO` and TAIEX (`^TWII`). If $< 52$ weekly pairs or the fetch fails → $\beta = 1.0$ (`beta_cadangan: true`, i.e. fallback beta) |
| `wacc_inputs` | `total_interest_expense` | Latest-year cash flow report | Interest expense of the last fiscal year |

### Handling Special Cases (Fail-Closed, No Guessing)
- **Financial-sector issuers** (`pasar.profil(kode)["keuangan"] == True`, industry code `17` on both TWSE and TPEx, e.g. `2881` Fubon Financial, `2891` CTBC Financial): not calculated with an FCFF-based DCF model. `bangun(kode)` returns `{"tidak_berlaku": True, "alasan": ...}` (not applicable, with reason) and the Valuation tab shows the badge **Not applicable / 不適用 / Tidak berlaku** along with the explanation in 3 languages.
- **Insufficient data or negative FCFF**: if the cash flow report has fewer than 3 full fiscal years, the price/share count is unavailable, $\text{FCFF}_0 \le 0$, or $\text{EV} \le 0$, `bangun(kode)` returns `{"tidak_bisa_dihitung": True, "alasan": ...}` (cannot be calculated, with reason) without guessing figures.

---

## 3. Automatic vs Manual Comparison for `2330` (`--banding`)

Result of running `python3 scripts/valuasi_otomatis.py 2330 --banding`:

| Field | Automatic | Manual (`2330.json`) | Difference % | Explanation |
|---|---:|---:|---:|---|
| `market.price_per_share (NTD)` | 2,235.00 | 2,380.00 | -6.09% | Price on the latest trading date (`2026-11-09`) vs the date of the manual file (`2026-09-14`) |
| `market.shares_issued_thousands` | 25,932,370.1 | 25,932,524.0 | -0.00% | TWSE OpenAPI `t187ap03_L` (difference < 0.001%) |
| `balance_sheet.cash_and_equivalents (2025-12-31)` | **2,767,856.4** | **2,767,856.4** | **+0.00%** | **Exactly identical** (`CashAndCashEquivalents`) |
| `balance_sheet.short_term_investments (2025-12-31)` | **300,638.2** | **300,638.2** | **+0.00%** | **Exactly identical** (`FinancialAssetsAtAmortizedCost` 124,945.5 + `FVOCI` 175,692.7) |
| `balance_sheet.current_portion_lt_debt (2025-12-31)` | 0.0 | 136,926.5 | -100.00% | The FinMind `TaiwanStockBalanceSheet` dataset merges `一年內到期長期負債` (long-term liabilities due within one year) into `OtherCurrentLiabilities` |
| `balance_sheet.long_term_debt (2025-12-31)` | **896,062.0** | **896,062.0** | **+0.00%** | **Exactly identical** (`BondsPayable` 856,227.5 + `LongtermBorrowings` 39,834.5) |
| `cash_flow.cfo_by_year[2023]` | 1,241,967.3 | 1,600,000.0 | -22.38% | The manual file uses rounded **estimated** figures (see below) |
| `cash_flow.capex_by_year[2023]` | 949,816.8 | 1,313,000.0 | -27.66% | The manual file uses rounded **estimated** figures |
| `cash_flow.interest_expense_by_year[2023]` | 11,999.4 | 12,000.0 | -0.01% | Rounding in the manual file |
| `cash_flow.cfo_by_year[2024]` | 1,826,177.1 | 2,000,000.0 | -8.69% | The manual file uses rounded **estimated** figures |
| `cash_flow.capex_by_year[2024]` | 956,006.5 | 1,140,000.0 | -16.14% | The manual file uses rounded **estimated** figures |
| `cash_flow.interest_expense_by_year[2024]` | 10,495.3 | 12,000.0 | -12.54% | The manual file uses rounded **estimated** figures |
| `cash_flow.cfo_by_year[2025]` | **2,274,975.6** | **2,274,980.0** | **-0.00%** | Full 2025 annual report (rounding difference 0.0002%) |
| `cash_flow.capex_by_year[2025]` | **1,272,410.5** | **1,272,400.0** | **+0.00%** | Full 2025 annual report (rounding difference 0.0008%) |
| `cash_flow.interest_expense_by_year[2025]` | **12,370.4** | **12,300.0** | **+0.57%** | FinMind `InterestExpense` 2025 vs manual rounding (< 1%) |
| `tax.income_tax_expense` | 326,266.1 | 346,500.0 | -5.84% | Sum of the 4 quarters of FinMind `TAX` 2025 |
| `tax.pretax_income` | **2,041,662.8** | **2,041,600.0** | **+0.00%** | Sum of the 4 quarters of FinMind `PreTaxIncome` 2025 |
| `DCF: FCFF 2025 (fcff0)` | **1,012,958.7** | **1,012,792.4** | **+0.02%** | The difference is only **+0.02%** (< 1%) |
| `DCF: FCFF 3y average` | **731,393.2** | **726,573.1** | **+0.66%** | The difference is only **+0.66%** (< 1%) |
| `wacc_inputs.beta` | 1.0122 | 1.2500 | -19.02% | 2-year weekly regression (103 weeks vs `^TWII`) vs the Yahoo 5Y monthly beta in the manual file |
| `DCF: WACC` | 6.92% | 8.09% | -14.48% | Affected by the difference in $\beta$ (2Y weekly 1.0122 vs 5Y monthly 1.25) |
| `DCF: implied_growth (implied g)` | 5.02% | 6.29% | -20.27% | Both are above the perpetual growth ceiling of 3.50% (`exceeds_ceiling = True`) |

### Explanation of the 2023–2024 Differences and the Treatment of Current Debt (Item D-c)
1. **2023 and 2024 cash flows**: in `valuation/inputs/2330.json`, the note `sources.cash_flow` explicitly states: *"The 2023-2024 figures are tuned so that FCFF matches the finance team's hand calculation (297 and 870 bio) — ESTIMATES, must be replaced with real figures"*. Although the 2023–2024 CFO and Capex in the manual file are rounded estimated figures (`1,600,000` / `1,313,000` and `2,000,000` / `1,140,000`), the difference $\text{CFO} - \text{Capex}$ from the real audited FinMind figures gives a 2023 FCFF of `302.2` billion NTD (vs `297.0` billion manual) and a 2024 FCFF of `879.0` billion NTD (vs `870.0` billion manual), so the 3-year average FCFF differs by only **+0.66%**.
2. **`current_portion_lt_debt` and `short_term_borrowings` (D-c)**: the `TaiwanStockBalanceSheet` dataset in FinMind does not present the item `一年內到期長期負債` separately, but merges it into `OtherCurrentLiabilities` (`其他流動負債`). For `2330` (TSMC), the official MOPS audited report records the current portion of long-term debt at NT\$136,926.5 million. Without this item, the automatic debt of `2330` is recorded at NT\$896,062.0 million (`BondsPayable` + `LongtermBorrowings`), or about 13.25% lower than the actual interest-bearing debt (NT\$1,032,988.5 million). The short-term bank borrowings item (`ShorttermBorrowings` / `短期借款`) is now split out into the field `short_term_borrowings` (0.0 for `2330`) and computed in `scripts/dcf.py` (`debt = current_portion_lt_debt + long_term_debt + short_term_borrowings`). If the current portion of long-term debt is not available separately, the system flags that field in the list `"tidak_tersedia": ["current_portion_lt_debt"]` (unavailable) and shows a three-language warning in the Valuation tab. In the D-b integration, the manual worksheet fills in this unavailable field.

---


## 4. Evaluation of 10 Random Non-Financial Issuers (`--acak 10 --seed 7`)

Result of running `python3 scripts/valuasi_otomatis.py --acak 10 --seed 7 --simpan` (saved in [`eval/hasil/b2-2026-11-10.md`](../eval/hasil/b2-2026-11-10.md)):

| # | Code | Name | Exchange | Price (NTD) | Market Cap (Million NTD) | FCFF0 (Million NTD) | WACC | Beta (Fallback?) | Implied g | Status |
|---:|---|---|---|---|---:|---:|---:|---|---:|---|
| 1 | `3416` | Winmate | TWSE | 152.00 | 12,846.7 | 467.8 | 6.85% | 0.9663 (103w) | 2.74% | `ok` |
| 2 | `9939` | HON CHUAN | TWSE | 118.00 | 34,902.8 | 2,865.5 | 2.15% | 0.0472 (103w) | -4.12% | `ok` |
| 3 | `4506` | GFC | TPEx | 115.50 | 20,444.9 | 1,508.2 | 2.37% | 0.0861 (103w) | -5.95% | `ok` |
| 4 | `6811` | AEB | TPEx | 240.00 | 9,947.8 | 581.3 | 6.54% | 0.9174 (103w) | 0.07% | `ok` |
| 5 | `3346` | Laster Tech | TWSE | 18.50 | 2,242.7 | 252.9 | 3.58% | 1.0259 (103w) | -2.63% | `ok` |
| 6 | `8433` | BON FAME | TPEx | 49.10 | 2,676.2 | 8.5 | 3.26% | 0.1941 (103w) | 2.83% | `ok` |
| 7 | `1708` | SESODA | TWSE | 46.00 | 11,454.1 | 1,280.7 | 4.20% | 0.4519 (103w) | -5.61% | `ok` |
| 8 | `1560` | KINIK | TWSE | 735.00 | 110,462.8 | 895.3 | 9.25% | 1.4897 (103w) | 8.38% | `ok` |
| 9 | `5285` | Jih Lin | TWSE | 72.30 | 7,377.6 | 347.5 | 6.03% | 0.9697 (103w) | 1.25% | `ok` |
| 10 | `6173` | P.D.C. | TPEx | 208.00 | 33,473.0 | 769.4 | 12.04% | 2.0159 (103w) | 9.44% | `ok` |

In addition, issuers that happened to have $\text{FCFF}_0 \le 0$ in fiscal year 2025 when the sample was pulled (such as `6945`, `3049`, `1587`, `8068`, `6223`, `3234`) are honestly flagged as `tidak_bisa_dihitung` (cannot be calculated) together with their $\text{FCFF}_{2025}$ value, without producing a pseudo growth figure.

---

## 5. Findings for the technical team

Per the file-ownership rules, files outside B2/D3 ownership are not changed. Below are the findings on shared files that have already been handled on the `app/valuasi_otomatis.py` side, with suggested fixes if the technical team wants to tighten the core files:

1. **`scripts/dcf.py` line 141 (`rd = w["total_interest_expense"] / debt`)**
   - **Symptom**: Raises `ZeroDivisionError: float division by zero` for issuers with no interest-bearing debt (`current_portion_lt_debt + long_term_debt == 0`, for example `2305` 全友 or `1732` 毛寶).
   - **Current handling in `app/valuasi_otomatis.py`**: If total interest-bearing debt $= 0$, `long_term_debt` is set to $10^{-6}$ million NTD ($1\text{ NTD}$) and `total_interest_expense = 0.0` with the warning note `va.warn.tanpa_utang` (no debt), so $r_d = 0\%$, $w_e \approx 100\%$, and $\text{WACC} = r_e$.
   - **Suggestion for `scripts/dcf.py`**: Change line 141 to `rd = (w["total_interest_expense"] / debt) if debt > 0 else 0.0`.

2. **`scripts/dcf.py` line 66 (`tax["income_tax_expense"] / tax["pretax_income"]`)**
   - **Symptom**: Raises `ZeroDivisionError` if `pretax_income == 0`, or produces a negative / $>100\%$ effective tax rate if the issuer has a pre-tax loss (`pretax_income < 0`, for example `1467` 南緯).
   - **Current handling in `app/valuasi_otomatis.py`**: If `pretax_income <= 0`, `income_tax_expense < 0`, or `income_tax_expense >= pretax_income`, the effective tax shield is set to $0\%$ (`income_tax_expense = 0.0`, `pretax_income = max(abs(pretax_raw), 1.0)`) and given the warning `va.warn.pajak_tidak_normal` (abnormal tax).
   - **Suggestion for `scripts/dcf.py`**: Bound `effective_tax_rate` to the range $[0, 1]$ and handle `pretax_income <= 0` by returning `0.0`.

3. **`scripts/dcf.py` lines 99 & 167 (`implied_growth` and `circularity.drift_pct`)**
   - **Symptom**: If $\text{EV} \le 0$ (cash exceeds market capitalization plus debt) or $\text{FCFF}_0 \le 0$, `ev_from_growth()` can return `None`, so `abs(back - ev)` on line 167 raises `TypeError`.
   - **Current handling in `app/valuasi_otomatis.py`**: `bangun(kode)` first checks $\text{FCFF}_0 > 0$ and $\text{EV} > 0$ and returns the status `tidak_bisa_dihitung` with a three-language message before calling `dcf.compute()`.

4. **`app/main.py` line 234 (`watchlist()`)**
   - **Symptom**: `tervaluasi = set(store.emiten_tervaluasi())` only checks files in `valuation/inputs/*.json`, so the valuation indicator column on the `/watchlist` page only lights up for `2330` even though the automatic valuation cache in `DATA_DIR/valuasi_otomatis/` is already filled.
   - **Suggestion for `app/store.py` / `app/main.py`**: If the badge in `/watchlist` should also reflect issuers that already have a DCF-eligible automatic valuation, `store.emiten_tervaluasi()` can merge the codes from `VALUATION_DIR` and `valuasi_otomatis.CACHE_DIR` whose `layak_dcf(d) == True`.
