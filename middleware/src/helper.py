import numpy as np
from numpy import dot
import pandas as pd
import time
from performance_metrics import wealth_growth, realized_values

debug = False
CSV_FILE = "dataSang.csv"


def get_wealth(weights, returns, times, rebalance_dates):
    realized_return, realized_risk, realized_return_vector, sharpe = \
        realized_values(weights, returns, times, rebalance_dates)

    wealth_values, wealth_times = wealth_growth(returns, times, rebalance_dates,
                                                realized_return_vector, weights)
    return wealth_times, wealth_values


def get_data(tickers=None):
    import sys
    start = time.time()
    print(sys.path)
    if tickers is None:
        data = pd.read_csv(CSV_FILE, index_col=0)
    else:
        data = pd.read_csv(CSV_FILE, index_col=0)[tickers]
    end = time.time()
    print("Fetched data in {} sec".format(end - start))
    return data


def get_weights(prices, method='vanilla', estimation_horizon=225):

    prices = prices.dropna()
    returns_df = get_returns(prices)
    returns = returns_df.to_numpy()
    times = returns_df.index.values.astype('datetime64[D]')
    first_date = times[0]
    end_date = times[-1]
    start_invest_date = times[estimation_horizon + 1]

    times_int = (times - first_date).astype(int)
    rebalance_dates = np.arange(start_invest_date, end_date, dtype='M8[M]')

    rebalance_int = (rebalance_dates - first_date).astype(int)
    rebalance_int = rebalance_int[rebalance_int > 0]
    n_periods = len(rebalance_int)
    n, p = returns.shape
    weights = np.zeros((n_periods, p), dtype=float)

    if method == 'vanilla':
        weights = predict_vanilla(n_periods, p, weights, returns, times_int, rebalance_int, 30, 1, 225)

    return weights, returns, times, rebalance_dates


def predict_concord(n_periods, p, weights, returns,
                    times_int,
                    rebalance_int,
                    rebalance_horizon=30,
                    coef_mu=1,
                    estimation_horizon=225):

    for period in range(n_periods):
        rb_int = rebalance_int[period]
        if not period % 50:
            print(period)
        m_returns = returns[times_int < rb_int, :][(-estimation_horizon - 1):]
        print(m_returns.shape)
        w = concord_weights(m_returns)
        weights[period, :] = w.ravel()

    return weights


def predict_basic(n_periods, p, weights, returns,
                  times_int,
                  rebalance_int,
                  rebalance_horizon=30,
                  coef_mu=1,
                  estimation_horizon=225):

    weights = np.ones((n_periods, p), dtype=float) / p

    return weights


def predict_vanilla(n_periods, p, weights, returns,
                    times_int,
                    rebalance_int,
                    rebalance_horizon=30,
                    coef_mu=1,
                    estimation_horizon=225):

    for period in range(n_periods):
        rb_int = rebalance_int[period]
        if not period % 50:
            print(period)
        m_returns = returns[times_int > rb_int][(-estimation_horizon - 1):]

        s = np.cov(m_returns.T)
        w = np.linalg.solve(s, np.ones(p))
        m_weights = w / np.sum(w)
        weights[period, :] = m_weights.ravel()

    return weights


def get_w_eff(mu, omega, mu_star, vector=None):
    """Given a mean and a covariance calculate the efficient portfolio
    weights
    mu : mean vector of length p
    omega : covariance matrix size p-by-p
    mu_star : scalar, target returns

    """
    if vector is None:
        vector = np.ones((omega.shape[0], 1))

    omega_one = np.squeeze(dot(omega, vector))
    omega_mu = np.squeeze(dot(omega, mu))

    a = float(dot(omega_mu, vector))
    b = float(dot(omega_mu, mu))
    c = float(dot(dot(vector.T, omega), vector))

    d = b * c - a**2

    w_eff = (b * omega_one - a * omega_mu + mu_star *
             (c * omega_mu - a * omega_one)) / d

    return np.squeeze(w_eff)


def get_returns(prices):
    r = np.diff(prices, axis=0) / prices[:-1]
    r.index = prices.index[1:]
    return r


def get_w_min(omega, vector=None):
    if vector is None:
        vector = np.ones((omega.shape[0], 1))

    coef = 1 / np.dot(np.dot(vector.T, omega), vector)
    weights = coef * np.dot(omega, vector)

    return weights
