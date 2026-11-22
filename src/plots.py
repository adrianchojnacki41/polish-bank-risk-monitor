
import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy import stats
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.abspath(".."))
from src.build_dataset import build_dataset
from src.returns import prices_wide,log_returns


def plot_pdf_cdf(dist, x_min: float, x_max: float, title:str) -> plt.Figure:
    """ PDF and CDF of a scipy distribution side by side on [x_min, x_max]. """
    x = np.linspace(x_min, x_max, 500)
    fig,axes = plt.subplots(1,2, figsize = (11,5))
    axes[0].plot(x, dist.pdf(x))
    axes[0].set_title("PDF")
    axes[0].set_xlabel("x")

    axes[1].plot(x,dist.cdf(x))
    axes[1].set_title("CDF")
    axes[1].set_xlabel("x")
    fig.suptitle(title)
    fig.tight_layout()
    return fig        

def plot_return_hist(returns: pd.Series, log_scale: bool = False) -> plt.Figure:
    """Density histogram of returns with fitted normal and Student t densities."""
    returns_ = returns.dropna()
    fig, ax = plt.subplots(1, 1, figsize=(11, 5))

    returns_.plot.hist(bins=100, density=True, ax=ax, alpha=0.5, label="data")

    x = np.linspace(returns_.min(), returns_.max(), 500)

    mu, sigma = returns_.mean(), returns_.std()
    ax.plot(x, stats.norm.pdf(x, loc=mu, scale=sigma), label="normal")

    df, loc, scale = stats.t.fit(returns_)
    ax.plot(x, stats.t.pdf(x, df, loc=loc, scale=scale), label=f"Student t (df={df:.1f})")

    ax.set_title(f"Daily log returns: {returns.name}")
    ax.set_xlabel("return")
    ax.set_ylabel("density")
    ax.legend()

    if log_scale:
        ax.set_yscale("log")

    return fig

def plot_qq(returns: pd.Series) -> plt.Figure:
    """Q-Q plot of standardised returns against the standard normal distribution."""
    returns_ = returns.dropna()
    z = (returns_ - returns_.mean()) / returns_.std()

    sample_q = np.sort(z.to_numpy())
    n = len(sample_q)
    probs = (np.arange(1, n + 1) - 0.5) / n
    normal_q = stats.norm.ppf(probs)

    fig, ax = plt.subplots(1, 1, figsize=(7, 7))
    ax.scatter(normal_q, sample_q, s=8, alpha=0.5, label="data")

    lim = max(abs(normal_q).max(), abs(sample_q).max())
    ax.plot([-lim, lim], [-lim, lim], color="red", linewidth=1, label="y = x")

    ax.set_title(f"Q-Q plot vs normal: {returns.name}")
    ax.set_xlabel("normal quantiles")
    ax.set_ylabel("standardised return quantiles")
    ax.legend()
    return fig


def plot_rolling_vol(vol: pd.DataFrame) -> plt.Figure:
    """Annualised rolling volatility over time, one line per column."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    vol.plot(ax=ax, linewidth=1)

    ax.set_title("Rolling annualised volatility")
    ax.set_xlabel("date")
    ax.set_ylabel("annualised volatility")
    ax.legend(loc="upper left", ncol=3)
    return fig
