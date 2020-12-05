import numpy as np
from concord import concord, robust_selection

def get_weights(prices, method='vanilla', estimation_horizon=225):

    prices = prices.dropna()
    returns_df = get_returns(prices)
    returns = returns_df.to_numpy()
    times = returns_df.index.values.astype('datetime64[D]')
    first_date = times[0]
    end_date = times[-1]
    start_invest_date = times[estimation_horizon + 1]

    times_int = (times - first_date).astype(int)
    rebalance_dates = np.arange(start_invest_date, end_date, dtype='M8[M]').astype("M8[D]")

    rebalance_int = (rebalance_dates - first_date).astype(int)
    rebalance_int = rebalance_int[rebalance_int > 0]
    n_periods = len(rebalance_int)
    n, p = returns.shape
    weights = np.zeros((n_periods, p), dtype=float)

    if method == 'vanilla':
        weights = predict_vanilla(n_periods, p, weights, returns, times_int, rebalance_int, 30, 1, 225)
    elif method == 'concord':
        weights = predict_concord(n_periods, p, weights, returns, times_int, rebalance_int, 30, 1, 225)

    return weights, returns, times, rebalance_dates


def robust_concord_weights(returns, coef_mu=1):
    """Cross-validate to find the best penalty and then compute the
    weights

    Parameters
    ----------
    returns -- Matrix of returns
    """
    # compute returns

    
    optimal_lambda = robust_selection(returns)
    omega_hat, w_eff = get_weights_from_lambda(returns, optimal_lambda)
    
    return (w_eff, optimal_lambda)


def concord_weights(returns):
    weights, lambda_robust = robust_concord_weights(returns)
    
    return np.array(weights)


def predict_concord(n_periods, p, weights, returns,
                    times_int,
                    rebalance_int,
                    rebalance_horizon=30,
                    coef_mu=1,
                    estimation_horizon=225):

    # for period in range(n_periods):
    
    m_returns = []
    for period in range(n_periods):
        rb_int = rebalance_int[period]
        m_returns.append(returns[times_int < rb_int, :][(-estimation_horizon - 1):])

    for period in range(n_periods):
        rb_int = rebalance_int[period]

        m_returns = returns[times_int < rb_int, :][(-estimation_horizon - 1):]
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

    omega_one = np.squeeze(np.dot(omega, vector))
    omega_mu = np.squeeze(np.dot(omega, mu))

    a = float(np.dot(omega_mu, vector))
    b = float(np.dot(omega_mu, mu))
    c = float(np.dot(np.dot(vector.T, omega), vector))

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


def scale(data):
    res = data.copy()
    for i in range(res.shape[1]):
        s = np.std(res[:, i])
        m = np.mean(res[:, i])
        res[:, i] = (res[:, i] - m) / s

    return res


def row_diff(x):
    # MUST BE A FORTRAN ARRAY
    # see https://docs.scipy.org/doc/numpy/reference/generated/numpy.asfortranarray.html#numpy.asfortranarray
    n, p = x.shape
    d = np.zeros((n - 1, p))
    for i in range(p):
        d[:, i] = np.diff(x[:, i])

    return d

def get_weights_from_lambda(returns, optimal_lambda):
    omega_hat = concord(returns, optimal_lambda).todense()
    vector = np.ones((omega_hat.shape[0], 1))
    coef = 1 / np.dot(np.dot(vector.T, omega_hat), vector)
    w_eff = float(coef) * np.dot(omega_hat, vector)
    return omega_hat, w_eff


def cross_validate_sub(x_train, x_test, p, lambdas):
    n_lambdas = len(lambdas)
    rss = np.zeros(n_lambdas)
    sparsity = np.zeros(n_lambdas)
    for j, lam in enumerate(lambdas):
        n_test, p_test = x_test.shape
        n_train, p_train = x_train.shape
        omega_hat = concord(x_train, lam).todense()
        nnz = len(omega_hat.nonzero()[0])
        sparsity[j] = 1 - (nnz - p) / float((p * (p - 1)))
        omega_d = np.diag(np.diag(omega_hat))
        beta_hat = -np.dot(omega_d, omega_hat - omega_d)

        a = np.diag(np.ones(p_test)) - beta_hat
        residuals = np.dot(x_test, a.T)
        rss[j] = np.linalg.norm(residuals) / float(n_test)

    if np.isnan(rss[0]):
        raise ValueError("""Residuals after covariance estimate are zero.
            Something is wrong""")
    return rss, sparsity


# @njit
def col_mean(x):
    p = x.shape[1]
    mean = np.zeros(p)
    for i in range(p):
        mean[i] = np.mean(x[:, i])

    return mean


# @njit
def col_std(x):
    p = x.shape[1]
    std = np.zeros(p)
    for i in range(p):
        std[i] = np.std(x[:, i])

    return std


# @njit
def cross_validate(data,
                   lambdas=np.exp(np.linspace(np.log(5e-3), np.log(5e-1), 25)),
                   n_folds=10):
    """Cross-Validate lambda parameter for covariance estimate

    Parameters
    ----------
    data : A np.array of size n-by-p.
    lambdas : Set of penalty parameters;
    n_folds: Int,
    Number of folds to use, the data is divided into blocks to
    account for potential autocorrelation

    Returns
    -------
    optimal_lambda: double,
    The optimal value for lambda
    """
    # Create equally many labels for each fold id
    n_samples, n_features = data.shape
    samples_per_fold = int(np.ceil(n_samples / float(n_folds)))
    labels = np.arange(n_folds)
    idx_label = np.outer(labels, np.ones(samples_per_fold)).ravel()
    # Remove some indeces from the last label so that the indeces
    # have the same number of entries as the data
    diff = len(idx_label) - n_samples
    idx_label = idx_label[:-diff]
    n_lambdas = len(lambdas)
    rss = np.zeros((n_folds, n_lambdas))
    sparsity = np.zeros((n_folds, n_lambdas))

    for fold in range(n_folds):
        x_train = data[idx_label != fold, :]
        x_test = data[idx_label == fold, :]
        r = cross_validate_sub(x_train, x_test, n_features, lambdas)
        rss[fold, :], sparsity[fold, :] = r[0], r[1]

    # rss_ols = np.full((n_folds, 1), np.nan)
    # for fold in np.arange(n_folds):
    # omega_ols = np.linalg.inv(np.dot(x_train.T, x_train) / n_train)
    # beta_ols = -np.dot(np.diag(1/np.diag(omega_ols)), omega_ols)
    # a_ols = np.diag(np.ones(n_features)) - beta_ols + np.diag(np.diag(beta_ols))
    # rss_ols[fold] = np.linalg.norm(np.dot(x_test, a_ols.T), 'fro') / n_test

    mean_rss = col_mean(rss)
    mean_sparsity = col_mean(sparsity)
    std_rss = col_std(rss) / np.sqrt(n_folds)
    std_sparsity = col_std(sparsity)
    # mean_rss_ols = np.mean(rss_ols)
    lambda_min = lambdas[np.argmin(mean_rss)]
    print(mean_rss)
    if np.isnan(mean_rss[0]):
        from pdb import set_trace
        set_trace()
    lambda_1sd = np.max(lambdas[mean_rss < np.min(mean_rss) + std_rss])

    return lambda_min, lambda_1sd, mean_sparsity, std_sparsity, mean_rss, std_rss


if __name__ == '__main__':
    from test_main import mock_df
    prices = mock_df.loc[:'2009-09', :].to_numpy()
    returns = np.diff(prices, axis=0) / prices[:-1, :]
    concord_weights(np.array(returns))
