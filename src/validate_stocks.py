import pandas as pd
import numpy as np

STOCK_COLUMNS = ["date", "ticker", "currency", "open", "high", "low", "close", "adjclose", "volume"]
STOCK_NUMERIC_COLUMNS = ["open", "high", "low", "close", "adjclose", "volume"]
STOCK_STRING_COLUMNS = ["ticker"]
STOCK_DATE_COLUMNS = ["date"]
STOCK_PRICE_COLUMNS = ["open", "high", "low", "close", "adjclose"]
STOCK_DATE_COLUMN = "date"
STOCK_ID_COLUMN = "ticker"
fx_COLUMNS = ["date", "currency", "rate"]
fx_NUMERIC_COLUMNS = ["rate"]
fx_STRING_COLUMNS = ["currency"]
fx_DATE_COLUMNS = ["date"]
fx_PRICE_COLUMNS = ["rate"]
fx_DATE_COLUMN = "date"
fx_ID_COLUMN = "currency"

def _check_requirement_columns(
    df: pd.DataFrame,
    expected_columns: list[str],
    name: str)-> None:
    """Raise ValueError if any required column is missing from df. """
    missing_cols = set(expected_columns) - set(df.columns)
    
    if missing_cols:
        raise ValueError(f"{name}: missing columns {sorted(missing_cols)}. Check data!")


def _check_column_types(
    df: pd.DataFrame,
    numeric_cols: list[str] | None,
    string_cols: list[str] | None,
    date_cols: list[str] | None,
    name:str
)->None:
    """ Raise TypeError if any column contains unexpected data type. """

    for col in numeric_cols or []:
        if not np.issubdtype(df[col].dtype, np.number):
            raise TypeError(f"{name}: column '{col}' must be numeric, got {df[col].dtype}")

    for col in string_cols or []:
        if not df[col].map(lambda v: isinstance(v, str)).all():
            raise TypeError(f"{name}: column '{col}' must contain only strings")

    for col in date_cols or []:
        if not pd.api.types.is_datetime64_any_dtype(df[col]):
            raise TypeError(f"{name}: column '{col}' must be datetime, got {df[col].dtype}")


def _check_if_prices_are_positive(
    df: pd.DataFrame,
    prices_col: list[str],
    name: str
)->None:
    """ Raises ValueError if any column with prices is not positive. """
    if prices_col is None:
        raise ValueError(f"Argument prices_col is None")
        
    _check_requirement_columns(df, prices_col, name)

    for col in prices_col:
        if len(df[df[col]<=0]) > 0:
            raise ValueError(f"{col} in {name} does not have only positive values. Count of errors : {len(df[df[col]<=0])}")


def _check_dates(
    df: pd.DataFrame,
    date_col: str,
    name: str
)->None:
    """Raise ValueError if any date is later than today. """
    
    _check_requirement_columns(df, [date_col], name)
    today = pd.Timestamp.today().normalize()
    n_future = len(df[df[date_col]>today])
    if n_future:
        raise ValueError(f"{name}: {n_future} dates are later than today. Check data!")


def _check_duplicates(
    df: pd.DataFrame,
    date_col: str,
    ind_col: str,
    name: str,
)->None:
    """Raise ValueError if duplicates in date column for each ticker/currency. """
    
    _check_requirement_columns(df, [date_col,ind_col], name)
    
    n_duplicates = df.groupby(ind_col).agg(
        duplicate_dates = (date_col, lambda s: s.duplicated().sum())).reset_index()
    duplicated = n_duplicates[n_duplicates["duplicate_dates"]>0]
    
    if len(duplicated)>0:
        raise ValueError(f"{name} contains duplicated value: {duplicated}")


def validate_stocks(df: pd.DataFrame, name: str = "stocks") -> None:
    """Raise an error if the cleaned stock table breaks any validation rule."""
    _check_requirement_columns(df, STOCK_COLUMNS, name)
    _check_column_types(df, STOCK_NUMERIC_COLUMNS, STOCK_STRING_COLUMNS, STOCK_DATE_COLUMNS, name)
    _check_if_prices_are_positive(df, STOCK_PRICE_COLUMNS, name)
    _check_dates(df, STOCK_DATE_COLUMN, name)
    _check_duplicates(df, STOCK_DATE_COLUMN, STOCK_ID_COLUMN, name)


def validate_fx(df: pd.DataFrame, name: str = "FX") -> None:
    """Raise an error if the cleaned stock table breaks any validation rule."""
    _check_requirement_columns(df, fx_COLUMNS, name)
    _check_column_types(df, fx_NUMERIC_COLUMNS, fx_STRING_COLUMNS, fx_DATE_COLUMNS, name)
    _check_if_prices_are_positive(df, fx_PRICE_COLUMNS, name)
    _check_dates(df, fx_DATE_COLUMN, name)
    _check_duplicates(df, fx_DATE_COLUMN, fx_ID_COLUMN, name)
