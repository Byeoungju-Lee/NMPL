---
name: analyze-nvda-stock
description: Run the local NMPL stock analysis workflow for a requested ticker. Use when the user asks in Korean or English to analyze a stock ticker, especially phrases like "NVDA 주가 분석해줘", "AAPL 주가 분석해줘", "엔비디아 주가 분석", or "analyze AAPL stock"; extract the ticker, execute the NMPL folder's get_nvidia_price.py script, report generated outputs, summarize datacenter cell_value trends, compare datacenter P trends with monthly ticker closes, and compare the latest close against 30-day Bollinger bands.
---

# Analyze Stock Ticker

Run the existing local workflow instead of rewriting the analysis.

## Workflow

1. Use the NMPL workspace at `C:\Users\user\Dacon_base\내 PC (pc01)\Desktop\NMPL`.
2. Extract the ticker from the user request:
   - For requests like `AAPL 주가 분석해줘`, use `AAPL`.
   - For requests like `analyze MSFT stock`, use `MSFT`.
   - If no ticker is explicit, default to `NVDA`.
   - Normalize the ticker to uppercase before using it.
3. Execute `get_nvidia_price.py`.
4. If the user did not specify a month range, provide `5` for the first input. Provide the extracted ticker for the second input.

```text
5
{TICKER}
```

5. After execution, summarize the console output briefly. The script may still print an NVDA quote first because of `get_nvidia_quote()`; use the generated CSV and chart for the requested ticker analysis.
6. Mention generated files that exist, especially:
   - `{TICKER}_price.csv`
   - `datacenter_ppi.csv`
   - `datacenter_ppi.png`
   - `{TICKER}_candle_chart.png`
7. Read `datacenter_ppi.csv` and analyze the first 5 data rows. Treat this as the generated datacenter CSV if the user refers to `datacenter.csv`.
8. For those first 5 rows, focus on the `time` and `cell_value` columns:
   - Convert `cell_value` to numeric before comparing values.
   - The CSV is usually saved with the latest month first. For a trend explanation, reorder those 5 rows by `time` ascending before describing month-to-month movement.
   - Report whether `cell_value` is generally rising, falling, or mixed over those 5 months.
   - Include the starting value, ending value, net change, and notable month-to-month increases or decreases.
   - Keep the explanation concise and in Korean when the user asks in Korean.
9. Before the Bollinger band signal, compare the datacenter `P` trend with the requested ticker close trend:
   - In `datacenter_ppi.csv`, keep rows where `data_type_code` is `P` if that column exists.
   - Use `time` as the monthly key and numeric `cell_value` as the datacenter series.
   - In `{TICKER}_price.csv`, convert `Date_` to datetime and create a `YYYY-MM` monthly key.
   - For each month, use the last available trading day's `Close_{TICKER}` as the monthly close.
   - Join the two monthly series on the shared `YYYY-MM` month.
   - Before reporting the alignment result or Bollinger band signal, show a compact table with each overlapping month, datacenter `P`, `{TICKER}` monthly close, and the close date used.
   - Compare month-to-month directions: `cell_value` delta sign vs monthly close delta sign.
   - Report the direction match rate as `matching_directions / comparable_month_changes * 100`.
   - If at least 3 overlapping months exist, also report the Pearson correlation between `cell_value` and monthly close; otherwise say there are too few overlapping months for correlation.
   - Briefly state whether the datacenter `P` trend and `{TICKER}` close trend are strongly aligned, partially aligned, weakly aligned, or moving differently.
10. Read `{TICKER}_price.csv` and analyze the latest row by `Date_`. If that file is missing, fall back to `nvidia_price.csv` for older script versions.
11. For that latest row, compare `Close_{TICKER}` with `Lower_Band_` and `Upper_Band_`:
   - Convert `Date_` to datetime and choose the row with the most recent date.
   - Convert `Close_{TICKER}`, `Lower_Band_`, and `Upper_Band_` to numeric.
   - If `Close_{TICKER}` is missing, inspect the CSV headers and use the only `Close_*` column if it matches the requested ticker data.
   - Calculate `lower_distance_ratio = abs(Close_{TICKER} - Lower_Band_) / Close_{TICKER} * 100`.
   - Calculate `upper_distance_ratio = abs(Upper_Band_ - Close_{TICKER}) / Close_{TICKER} * 100`.
   - Report both ratios as percentages.
   - If the lower band ratio is smaller than or equal to the upper band ratio, say: "30일 기준 하한 밴드가 {TICKER} 주가와 가까워졌기에 매수 추천함."
   - If the upper band ratio is smaller, say: "30일 기준 상한 밴드와 {TICKER} 주가가 가까워졌으므로 매도 추천함."
   - Present this as a rule-based band signal from the CSV, not as comprehensive financial advice.

## Command

Prefer a PowerShell command equivalent to:

```powershell
"5`n{TICKER}`n" | python get_nvidia_price.py
```

If `python` is unavailable, try the environment's available Python runner. If dependencies or network access fail, report the exact blocker and the command attempted.

## Datacenter CSV Trend Summary

Use a concise process equivalent to:

```powershell
Import-Csv datacenter_ppi.csv |
  Select-Object -First 5 |
  Sort-Object time |
  Select-Object time, cell_value
```

Then explain the `cell_value` trend in plain Korean. For example: "첫 5개월 데이터는 2026-01부터 2026-05까지 전반적으로 상승했고, 중간에 2026-02에서 2026-03으로 소폭 하락한 뒤 다시 증가했습니다."

## Datacenter P vs Ticker Close Alignment

Compare the generated datacenter `P` series with `{TICKER}` monthly closes before calculating the latest Bollinger band signal.

Use the first 5 datacenter rows by file order for the short trend summary, but use all overlapping months available in both files for the alignment calculation unless the user asks for only the first 5 months.

Use a process equivalent to:

```text
datacenter_month = datacenter_ppi.time
datacenter_value = numeric datacenter_ppi.cell_value where data_type_code == "P"
ticker_month = Date_.strftime("%Y-%m")
ticker_monthly_close = last Close_{TICKER} by ticker_month
joined = inner join on month
```

Before the alignment explanation and before the Bollinger band signal, show the joined monthly table:

```text
month | P | Close_{TICKER} | Close_Date
```

Use the close date from the last available trading day in each month. Keep numeric values rounded to 2 decimals for close prices.

Then calculate:

```text
direction_match_rate = count(sign(diff(datacenter_value)) == sign(diff(ticker_monthly_close))) / count(comparable monthly changes) * 100
correlation = pearson(datacenter_value, ticker_monthly_close) when overlapping months >= 3
```

Explain the result in Korean with the number of overlapping months, the direction match rate, and correlation if available. Treat exact zero deltas as neutral; do not count neutral months as a match unless both series are neutral.

## Bollinger Band Signal

Use a concise process equivalent to:

```powershell
$ticker = "{TICKER}"
$closeCol = "Close_$ticker"
Import-Csv "{TICKER}_price.csv" |
  Where-Object { $_.$closeCol -and $_.Lower_Band_ -and $_.Upper_Band_ } |
  Sort-Object {[datetime]$_.Date_} -Descending |
  Select-Object -First 1 Date_, $closeCol, Lower_Band_, Upper_Band_
```

Calculate the distance ratios from the latest close:

```text
lower_distance_ratio = abs(Close_{TICKER} - Lower_Band_) / Close_{TICKER} * 100
upper_distance_ratio = abs(Upper_Band_ - Close_{TICKER}) / Close_{TICKER} * 100
```

Then state which band is closer and include the matching Korean recommendation sentence from the workflow.
