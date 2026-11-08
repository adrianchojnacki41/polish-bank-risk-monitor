from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
NBP_URL = "https://api.nbp.pl/api/exchangerates/rates/a/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

START_DATE = "2015-01-01"

TICKERS = {
    "PKO BP": "PKO.WA",
    "Pekao": "PEO.WA",
    "mBank": "MBK.WA",
    "ING": "ING.WA",
    "Millennium": "MIL.WA",
    "Alior": "ALR.WA",
}

CURRENCIES = ["EUR", "CHF", "USD"]