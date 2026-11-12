import pandas as pd

from src.cleaning import clean_fx, clean_stocks
from src.config import PROCESSED_DIR
from src.data_loader import load_fx, load_stocks
from src.validate import validate_fx, validate_stocks


def build_dataset(refresh: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load, clean and validate stocks and FX rates, then save them to data/processed."""
    stocks = clean_stocks(load_stocks(refresh))
    validate_stocks(stocks)

    fx = clean_fx(load_fx(refresh))
    validate_fx(fx)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    stocks.to_csv(PROCESSED_DIR / "stocks_clean.csv", index=False)
    fx.to_csv(PROCESSED_DIR / "fx_clean.csv", index=False)

    return stocks, fx
