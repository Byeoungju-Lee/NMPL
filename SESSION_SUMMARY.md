# Session Summary

## Workspace

- Path: `C:\Users\user\Dacon_base\내 PC (pc01)\Desktop\NMPL`
- Main script: `get_nvidia_price.py`
- Skill files:
  - `C:\Users\user\.codex\skills\analyze-nvda-stock\SKILL.md`
  - `SKILL.md` in this workspace as a synchronized copy

## Skill Purpose

The `analyze-nvda-stock` skill now runs the local stock analysis workflow for a requested ticker, not only NVDA.

Examples:

```text
NVDA 주가 분석해줘 -> NVDA
AAPL 주가 분석해줘 -> AAPL
MSFT 주가 분석해줘 -> MSFT
```

If no ticker is explicit, the skill defaults to `NVDA`.

## Current Workflow

1. Extract `{TICKER}` from the user request and uppercase it.
2. Execute `get_nvidia_price.py`.
3. If no month range is specified, provide stdin:

```text
5
{TICKER}
```

4. Report generated files:

```text
{TICKER}_price.csv
datacenter_ppi.csv
datacenter_ppi.png
{TICKER}_candle_chart.png
```

5. Summarize the first 5 datacenter rows by `time` and `cell_value`.
6. Before the Bollinger band signal, show the joined monthly table:

```text
month | P | Close_{TICKER} | Close_Date
```

7. Compare datacenter `P` trend with `{TICKER}` monthly closes:
   - Monthly key: `YYYY-MM`
   - Datacenter value: `cell_value` where `data_type_code == "P"`
   - Ticker close: last available trading day close for each month
   - Metrics: direction match rate and Pearson correlation when at least 3 overlapping months exist

8. Calculate latest Bollinger band signal:

```text
lower_distance_ratio = abs(Close_{TICKER} - Lower_Band_) / Close_{TICKER} * 100
upper_distance_ratio = abs(Upper_Band_ - Close_{TICKER}) / Close_{TICKER} * 100
```

If lower band is closer:

```text
30일 기준 하한 밴드가 {TICKER} 주가와 가까워졌기에 매수 추천함.
```

If upper band is closer:

```text
30일 기준 상한 밴드와 {TICKER} 주가가 가까워졌으므로 매도 추천함.
```

## Verified Runs

### NVDA

- Generated: `NVDA_price.csv`, `NVDA_candle_chart.png`, `datacenter_ppi.csv`, `datacenter_ppi.png`
- Latest row:
  - Date: `2026-07-02`
  - Close_NVDA: `194.83`
  - Lower_Band_: `190.14`
  - Upper_Band_: `225.87`
  - Lower distance: `2.40%`
  - Upper distance: `15.93%`
  - Signal: lower band closer, buy recommendation sentence

Datacenter P vs NVDA monthly close table used:

| month | P | Close_NVDA | Close_Date |
|---|---:|---:|---|
| 2025-11 | 35281 | 176.77 | 2025-11-28 |
| 2025-12 | 34030 | 186.27 | 2025-12-31 |
| 2026-01 | 33823 | 190.90 | 2026-01-30 |
| 2026-02 | 34205 | 176.97 | 2026-02-27 |
| 2026-03 | 34019 | 174.20 | 2026-03-31 |
| 2026-04 | 34204 | 199.34 | 2026-04-30 |
| 2026-05 | 34311 | 210.89 | 2026-05-29 |

- Overlapping months: `7`
- Direction match rate: `50.00%`
- Pearson correlation: `-0.204`

### AAPL

- Generated: `AAPL_price.csv`, `AAPL_candle_chart.png`, `datacenter_ppi.csv`, `datacenter_ppi.png`
- Latest row:
  - Date: `2026-07-02`
  - Close_AAPL: `308.63`
  - Lower_Band_: `279.37`
  - Upper_Band_: `319.81`
  - Lower distance: `9.48%`
  - Upper distance: `3.62%`
  - Signal: upper band closer, sell recommendation sentence

Datacenter P vs AAPL monthly close table used:

| month | P | Close_AAPL | Close_Date |
|---|---:|---:|---|
| 2025-11 | 35281 | 278.33 | 2025-11-28 |
| 2025-12 | 34030 | 271.36 | 2025-12-31 |
| 2026-01 | 33823 | 259.00 | 2026-01-30 |
| 2026-02 | 34205 | 263.94 | 2026-02-27 |
| 2026-03 | 34019 | 253.56 | 2026-03-31 |
| 2026-04 | 34204 | 271.10 | 2026-04-30 |
| 2026-05 | 34311 | 312.06 | 2026-05-29 |

- Overlapping months: `7`
- Direction match rate: `100.00%`
- Pearson correlation: `0.351`

### MSFT

- Generated: `MSFT_price.csv`, `MSFT_candle_chart.png`, `datacenter_ppi.csv`, `datacenter_ppi.png`
- Latest row:
  - Date: `2026-07-02`
  - Close_MSFT: `390.49`
  - Lower_Band_: `347.09`
  - Upper_Band_: `455.04`
  - Lower distance: `11.11%`
  - Upper distance: `16.53%`
  - Signal: lower band closer, buy recommendation sentence

## Notes

- `get_nvidia_price.py` still prints an NVDA quote first because it calls `get_nvidia_quote()` before asking for the ticker. The generated `{TICKER}_price.csv` and `{TICKER}_candle_chart.png` are the requested ticker outputs.
- Price CSV files now use `{TICKER}_price.csv`, not `nvidia_price.csv`.
- The Bollinger band recommendation is a CSV-based rule signal, not comprehensive financial advice.
