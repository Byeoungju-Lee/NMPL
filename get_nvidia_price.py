"""
Fetch NVIDIA stock data from Yahoo Finance.

Install dependency if needed:
    pip install yfinance pandas
"""

from __future__ import annotations

import yfinance as yf


def get_nvidia_quote() -> dict:
    ticker = yf.Ticker("NVDA")
    history = ticker.history(period="5d", interval="1d")

    if history.empty:
        raise RuntimeError("No price data returned from Yahoo Finance.")

    latest = history.tail(1).iloc[0]
    return {
        "symbol": "NVDA",
        "date": history.tail(1).index[0].strftime("%Y-%m-%d"),
        "open": float(latest["Open"]),
        "high": float(latest["High"]),
        "low": float(latest["Low"]),
        "close": float(latest["Close"]),
        "volume": int(latest["Volume"]),
    }


if __name__ == "__main__":
    quote = get_nvidia_quote()

    print(f"Symbol : {quote['symbol']}")
    print(f"Date   : {quote['date']}")
    print(f"Open   : {quote['open']:.2f}")
    print(f"High   : {quote['high']:.2f}")
    print(f"Low    : {quote['low']:.2f}")
    print(f"Close  : {quote['close']:.2f}")
    print(f"Volume : {quote['volume']:,}")
