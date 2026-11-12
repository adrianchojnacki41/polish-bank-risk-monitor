import pandas as pd
import pytest

from src.validate import validate_fx, validate_stocks


def valid_stocks() -> pd.DataFrame:
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
        "ticker": ["PKO BP", "PKO BP"],
        "currency": ["PLN", "PLN"],
        "open": [40.0, 41.0],
        "high": [41.0, 42.0],
        "low": [39.0, 40.0],
        "close": [40.5, 41.5],
        "adjclose": [40.5, 41.5],
        "volume": [1000, 1200],
    })


def valid_fx() -> pd.DataFrame:
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
        "currency": ["EUR", "EUR"],
        "rate": [4.30, 4.32],
    })


def test_valid_data_passes():
    validate_stocks(valid_stocks())
    validate_fx(valid_fx())


def test_missing_column_raises():
    df = valid_stocks().drop(columns="volume")
    with pytest.raises(ValueError):
        validate_stocks(df)


def test_wrong_type_raises():
    df = valid_stocks()
    df["ticker"] = [1, 2]
    with pytest.raises(TypeError):
        validate_stocks(df)


def test_negative_price_raises():
    df = valid_stocks()
    df.loc[0, "close"] = -1.0
    with pytest.raises(ValueError):
        validate_stocks(df)


def test_future_date_raises():
    df = valid_fx()
    df.loc[1, "date"] = pd.Timestamp.today().normalize() + pd.Timedelta(days=30)
    with pytest.raises(ValueError):
        validate_fx(df)


def test_duplicate_date_raises():
    df = pd.concat([valid_stocks(), valid_stocks().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError):
        validate_stocks(df)
