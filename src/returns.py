

import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.abspath(".."))
from src.build_dataset import build_dataset
from src.config import TRADING_DAYS
import scipy.stats as stats



def prices_wide(stocks: pd.DataFrame, value_col: str = "adjclose") -> pd.DataFrame:
    """Return a date × ticker table with values from value_col. """
    
    if value_col not in stocks.columns:
        raise ValueError(f"Can not find {value_col} in df")
        
    return stocks.pivot_table(value_col, "date", "ticker")
    

def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Return daily log returns ln(P_t / P_(t-1)) for each column; the first row is dropped."""   
    
    df = prices.copy()
    
    for col in df.columns:
        df[f"{col}_prev"] = df[col].shift(1)
        df[f"{col}"] = np.log(df[col] / df[f"{col}_prev"])
        df = df.drop([f"{col}_prev"],axis="columns")

    return df.iloc[1:]


def simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Return daily simple_returns _P_t / P_(t-1)) -1 for each column; the first row is dropped."""   
    
    df = prices.copy()
    
    for col in df.columns:
        df[f"{col}_prev"] = df[col].shift(1)
        df[f"{col}"] = (df[col] / df[f"{col}_prev"])-1
        df = df.drop([f"{col}_prev"],axis="columns")

    return df.iloc[1:]


def bank_index(simple_ret: pd.DataFrame) -> pd.Series:
    """ Equal-weighted daily average of bank simple returns, ignoring missing values."""
    return simple_ret.mean(axis = 1).dropna().rename("Bank index")


def describe_returns(returns: pd.DataFrame, periods_per_year: int = TRADING_DAYS) -> pd.DataFrame:
    """Summary statistics of returns for each column, with annualised volatility."""
    return pd.DataFrame({
        "n_days": returns.count(),
        "mean": returns.mean(),
        "std": returns.std(),
        "std_annual": returns.std() * np.sqrt(periods_per_year),
        "skew": returns.skew(),
        "excess_kurtosis": returns.kurt(),
        "min": returns.min(),
        "max": returns.max(),
    })


def normality_test(returns: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """Jarque-Bera normality test for each column."""
    bank = []
    jb_stat = []
    p_value = []
    reject_normality = []

    for col in returns.columns:
        jbt = stats.jarque_bera(returns[col].dropna())
        bank.append(col)
        jb_stat.append(jbt.statistic)
        p_value.append(jbt.pvalue)
        reject_normality.append(jbt.pvalue < alpha)

    return pd.DataFrame(
        {"jb_stat": jb_stat, "p_value": p_value, "reject_normality": reject_normality},
        index=bank,
    )


def rolling_volatility(
    returns: pd.DataFrame, window: int = 21, periods_per_year: int = TRADING_DAYS
) -> pd.DataFrame:
    """Annualised rolling volatility for each column; the first window - 1 rows are NaN."""
    return returns.rolling(window).std() * np.sqrt(periods_per_year)
