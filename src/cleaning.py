
import os
import sys

sys.path.append(os.path.abspath(".."))

import pandas as pd

from src.data_loader import load_fx, load_stocks

import matplotlib.pyplot as plt
from ipywidgets import interact

def clean_stocks(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean daily stock prices in long format.

    Rules:
    - drop rows with missing adjclose or close,
    - drop duplicated dates within a ticker (the last downloaded row is kept),
    - drop non-trading days: zero volume and close equal to the previous close of the same ticker.

    Returns a new DataFrame with the same columns, sorted by ticker and date.
    Raises ValueError if previous closes are missing beyond the first day of each ticker.
    """
    
    df = data.copy()
    df = df.sort_values(by = ["ticker","date"], kind="stable").reset_index(drop = True)
    
    df["date"] = pd.to_datetime(df["date"], format = "%Y-%m-%d")
    
    df = df.dropna(subset=["adjclose", "close"])

    df = df.drop_duplicates(subset = ["date","ticker"], keep = "last").reset_index(drop = True)
    
    df["prev_close"] = df.groupby("ticker")["close"].shift(1)

    if df["ticker"].nunique() != df["prev_close"].isna().sum():
        raise ValueError("Unexpected missing previous closes. Check data!")

    no_trading = (df["volume"] == 0) & (df["close"] == df["prev_close"])
    df = df[~no_trading]
    
    return df.drop(columns = "prev_close").reset_index(drop = True)


def clean_fx(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean daily NBP FX rates in long format.

    Rules:
    - drop rows with missing rate,
    - drop duplicated dates within a currency (the last downloaded row is kept).

    Returns a new DataFrame with the same columns, sorted by currency and date.
    """
    
    df = data.copy()
    df = df.sort_values(by = ["currency","date"], kind="stable").reset_index(drop = True)
    
    df["date"] = pd.to_datetime(df["date"], format = "%Y-%m-%d")
    
    df = df.dropna(subset = ["rate"])
    
    df = df.drop_duplicates(subset = ["date","currency"], keep = "last").reset_index(drop = True)
    
    return df
