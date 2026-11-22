# \# Polish Bank Risk Monitor

# 

# !\[tests](https://github.com/adrianchojnacki41/polish-bank-risk-monitor/actions/workflows/tests.yml/badge.svg)

# 

# Risk analysis of Polish bank stocks on real market data. The project downloads

# daily prices of six banks listed on the Warsaw Stock Exchange and NBP exchange

# rates, cleans and validates them, and measures how far bank returns are from

# the normal distribution. Work in progress: VaR, correlations and a Power BI

# dashboard are next.

# 

# \## Data

# 

# | Source | Content | Frequency |

# |---|---|---|

# | Yahoo Finance (chart API) | PKO BP, Pekao, mBank, ING, Millennium, Alior: open, high, low, close, adjusted close, volume | daily, from 2015-01-01 |

# | NBP API, table A | EUR, CHF and USD mid rates against PLN | daily, from 2015-01-01 |

# 

# Raw data is cached in `data/raw/`, cleaned data is saved to `data/processed/`.

# Neither folder is stored in the repository.

# 

# \*\*Cleaning rules\*\*

# \- rows sorted by ticker and date, dates converted to datetime

# \- rows without close or adjusted close removed

# \- duplicated (date, ticker) pairs removed, the last record is kept

# \- days without trading (volume 0 and price unchanged from the previous day) removed

# \- FX: rows without a rate and duplicated (date, currency) pairs removed

# 

# \*\*Validation\*\* (`validate.py`, covered by tests): required columns, column types,

# positive prices, no future dates, no duplicated (date, ticker) pairs.

# 

# \*\*Limitations\*\*

# \- Yahoo chart API is unofficial and may change without notice

# \- adjusted close relies on Yahoo's dividend and split adjustments

# \- Santander Bank Polska is not included yet

# \- stock and NBP calendars differ (some days have only one of the two)

# 

# \## Returns and distribution

# 

# Daily log returns of the six banks, about 2,960 trading days each.

# 

# Daily volatility ranges from 2.0% (ING) to 2.7% (Millennium), i.e. 31–42% a year.

# Every bank has strongly positive excess kurtosis, from 4.0 (ING) to 9.5 (Pekao):

# large daily moves, up to -24% in a single day, happen far more often than a normal

# distribution predicts. The Jarque-Bera test rejects normality for every bank

# (p < 0.001). Four of six banks also have negative skewness, so the largest moves

# tend to be drops. A VaR model that assumes normal returns will therefore

# understate tail risk.

# 

# | Bank | Days | Daily std | Annual std | Skew | Excess kurtosis | Worst day | Best day |

# |---|---|---|---|---|---|---|---|

# | Alior | 2958 | 2.55% | 40.5% | -0.28 | 6.83 | -22.2% | +16.5% |

# | ING | 2962 | 1.96% | 31.1% | 0.14 | 3.95 | -11.6% | +12.4% |

# | Millennium | 2962 | 2.67% | 42.3% | -0.35 | 6.90 | -24.0% | +16.7% |

# | PKO BP | 2962 | 2.04% | 32.4% | -0.32 | 5.61 | -18.4% | +12.5% |

# | Pekao | 2962 | 2.07% | 32.8% | -0.49 | 9.47 | -21.8% | +15.8% |

# | mBank | 2930 | 2.55% | 40.4% | 0.26 | 5.38 | -17.8% | +21.6% |

# 

# Worst and best day are log returns.

# 

# !\[Bank index daily log returns, log scale](images/index\_hist\_log.png)

# 

# Volatility is not constant: it jumps sharply in March 2020 for all banks.

# 

# !\[Rolling annualised volatility](images/rolling\_vol.png)

# 

# Full analysis: \[returns notebook](notebooks/03\_returns\_analysis.ipynb).

# 

# \## Modules

# 

# \- `config.py`: paths, tickers, currencies, API addresses, constants

# \- `data\_loader.py`: download from Yahoo and NBP with local CSV cache

# \- `cleaning.py`: cleaning rules for stock prices and FX rates

# \- `validate.py`: data quality checks

# \- `build\_dataset.py`: load, clean, validate and save the dataset

# \- `returns.py`: returns, bank index, summary statistics, normality test, rolling volatility

# \- `plots.py`: distribution, histogram, Q-Q and rolling volatility charts

# 

# \## How to run

# 

# &#x20;   pip install -r requirements.txt

# &#x20;   python -m pytest

# 

# In a notebook:

# 

# &#x20;   from src.build\_dataset import build\_dataset

# &#x20;   stocks, fx = build\_dataset()          # refresh=True downloads fresh data

