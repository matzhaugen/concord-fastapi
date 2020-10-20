import numpy as np
from concord import concord, robust_selection


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


def concord_weights(returns, coef_mu=1):
    """Cross-validate to find the best penalty and then compute the
    weights

    Parameters
    ----------
    returns -- Matrix of returns
    """
    # compute returns

    lambda_min, optimal_lambda, mean_sparsity, std_sparsity, mean_rss, std_rss = cross_validate(returns)
    omega_hat, w_eff = get_weights_from_lambda(returns, optimal_lambda)

    if coef_mu == 1:
        pass
    else:
        # mu_returns = self.get_mean(prices)
        # mu_min = float(dot(mu_returns, w_min))
        # mu = mu_min * coef_mu  # Try 2 first
        # w_eff = get_w_eff(mu_returns, omega_hat, mu)
        pass
    return (w_eff, lambda_min, optimal_lambda, omega_hat, mean_sparsity, std_sparsity,
            mean_rss, std_rss)


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
