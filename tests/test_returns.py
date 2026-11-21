import pandas as pd
import numpy as np
import os
import sys
from src.returns import prices_wide,simple_returns,log_returns


def test_constant_growth():
    """Prices rising 1% a day give simple returns 0.01 and log returns ln(1.01)."""
    prices = pd.DataFrame({"Bank_test": [100, 101, 102.01, 103.0301, 104.060401]})

    simple = simple_returns(prices)
    log = log_returns(prices)

    assert np.allclose(simple["Bank_test"], 0.01, atol=1e-12)
    assert np.allclose(log["Bank_test"], np.log(1.01), atol=1e-12)


def test_date_sort():  
    """ Testing if dates are sorted ascending """
    stocks = pd.DataFrame({
    "date": pd.to_datetime([
        "2025-01-03", "2025-01-01", "2025-01-02",
        "2025-01-03", "2025-01-01", "2025-01-02",
    ]),
    "ticker": ["A", "A", "A", "B", "B", "B"],
    "adjclose": [102.0, 100.0, 101.0, 52.0, 50.0, 51.0],
     })
    stocks_ = prices_wide(stocks)
    stocks_["date"] = stocks_.index
    stocks_["date_1"] = stocks_["date"].shift(1)
    stocks_ = stocks_.dropna()
    stocks_["diff"] = (stocks_["date"] - stocks_["date_1"]).dt.days
    min_diff = stocks_["diff"].min()
    
    assert min_diff > 0,"Dates are not sorted correctly"
