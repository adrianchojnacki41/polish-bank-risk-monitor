import time

import pandas as pd
import requests

from src.config import CURRENCIES, HEADERS, NBP_URL, RAW_DIR, START_DATE, TICKERS, YAHOO_URL


def _convert_yahoo_json(data: dict, ticker: str) -> pd.DataFrame:
    """Convert one Yahoo chart result into a daily price table."""
    meta = data["meta"]
    quote = data["indicators"]["quote"][0]
    adjclose = data["indicators"]["adjclose"][0]["adjclose"]

    return pd.DataFrame({
        "date": pd.to_datetime(data["timestamp"], unit="s").normalize(),
        "ticker": ticker,
        "currency": meta.get("currency"),
        "open": quote["open"],
        "high": quote["high"],
        "low": quote["low"],
        "close": quote["close"],
        "adjclose": adjclose,
        "volume": quote["volume"],
    })


def _convert_nbp_json(data: dict, currency: str) -> pd.DataFrame:
    """Convert one NBP response into a daily FX rate table."""
    df = pd.DataFrame(data["rates"])
    return pd.DataFrame({
        "date": pd.to_datetime(df["effectiveDate"]),
        "currency": currency,
        "rate": df["mid"],
    })


def download_stocks(
    tickers: dict[str, str] = TICKERS,
    start_date: str = START_DATE,
    end_date: str | None = None,
) -> pd.DataFrame:
    """Download daily prices from Yahoo Finance for several stocks, in long format."""
    if end_date is None:
        end_date = pd.Timestamp.today().normalize()

    start_date_int = int(pd.Timestamp(start_date).timestamp())
    end_date_int = int(pd.Timestamp(end_date).timestamp())

    params = {
        "period1": start_date_int,
        "period2": end_date_int,
        "interval": "1d",
    }

    frames = []
    for name, symbol in tickers.items():
        r = requests.get(YAHOO_URL + symbol, params=params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            raise ValueError(f"Failed to download {name} ({symbol}): HTTP {r.status_code}")

        chart = r.json()["chart"]
        if chart.get("result") is None:
            raise ValueError(f"No data for {name} ({symbol}): {chart.get('error')}")

        frames.append(_convert_yahoo_json(chart["result"][0], name))
        time.sleep(1)

    return pd.concat(frames, ignore_index=True)


def download_nbp_rates(
    currencies: list[str] = CURRENCIES,
    start_date: str = START_DATE,
    end_date: str | None = None,
) -> pd.DataFrame:
    """Download NBP table A mid rates for several currencies, in monthly chunks."""
    if end_date is None:
        end_date = pd.Timestamp.today().normalize()
    end_date = pd.Timestamp(end_date)

    frames = []
    for currency in currencies:
        chunk_start = pd.Timestamp(start_date)
        while chunk_start <= end_date:
            chunk_end = min(chunk_start + pd.DateOffset(months=1, days=-1), end_date)
            url = (
                f"{NBP_URL}{currency}/"
                f"{chunk_start.strftime('%Y-%m-%d')}/{chunk_end.strftime('%Y-%m-%d')}/?format=json"
            )
            r = requests.get(url, headers=HEADERS, timeout=10)

            if r.status_code == 200:
                frames.append(_convert_nbp_json(r.json(), currency))
            elif r.status_code != 404:
                raise ValueError(
                    f"Failed to download {currency} from {chunk_start.date()} "
                    f"to {chunk_end.date()}: HTTP {r.status_code}"
                )

            chunk_start = chunk_end + pd.Timedelta(days=1)
            time.sleep(0.5)

    return pd.concat(frames, ignore_index=True)


def _load_or_download(filename: str, download_fn, refresh: bool) -> pd.DataFrame:
    """Read a cached CSV from data/raw, or download, save and return fresh data."""
    path = RAW_DIR / filename

    if path.exists() and not refresh:
        return pd.read_csv(path, parse_dates=["date"])

    df = download_fn()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def load_stocks(refresh: bool = False) -> pd.DataFrame:
    """Bank stock prices: from cache if available, otherwise downloaded from Yahoo."""
    return _load_or_download("stocks.csv", download_stocks, refresh)


def load_fx(refresh: bool = False) -> pd.DataFrame:
    """NBP FX rates: from cache if available, otherwise downloaded from the NBP API."""
    return _load_or_download("fx_rates.csv", download_nbp_rates, refresh)
