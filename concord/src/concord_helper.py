import numpy as np
from concord import concord


def s_func(x, lam):
    result = np.sign(x) * np.maximum(np.absolute(x) - lam, 0)
    return result


def t_vector(w, s, lam):

    diag_s = np.diag(s)
    diag_s_matrix = np.diag(diag_s)
    sum_ii = np.einsum('ij,ij->i', w, s) - np.diag(w) * diag_s
    sum_ij = np.dot(w, s) - np.dot(w, diag_s_matrix)
    sum_ji = np.dot(w.T, s) - np.dot(w.T, diag_s_matrix)

    numerator_ii = -sum_ii + np.sqrt(sum_ii**2 + 4 * diag_s)
    numerator_ij = s_func(-(sum_ij + sum_ji), lam)

    denominator = np.add.outer(diag_s, diag_s)

    output = numerator_ij / denominator
    np.fill_diagonal(output, numerator_ii / np.diag(denominator))

    return output


def t(i, j, w, s, lam):

    if i == j:
        sub_w = np.delete(w[i, :], j)
        sub_s = np.delete(s[i, :], j)
        my_sum = np.dot(sub_w, sub_s)
        if s[i, i] == 0:
            raise ValueError("S_ii is zero")
        else:
            output = (-my_sum + np.sqrt(my_sum**2 + (4 * s[i, i]))) / (2 * s[i, i])
    else:
        my_sum1 = np.dot(np.delete(w[i, :], j), np.delete(s[j, :], j))
        my_sum2 = np.dot(np.delete(w[:, j], i), np.delete(s[i, :], i))
        output = s_func(- (my_sum1 + my_sum2), lam) / (s[i, i] + s[j, j])

    return output


def scale(data):
    res = data.copy()
    for i in range(res.shape[1]):
        s = np.std(res[:, i])
        m = np.mean(res[:, i])
        res[:, i] = (res[:, i] - m) / s

    return res


# def concord(data, lam, tol=1e-5, maxit=100):
#     x = scale(data)
#     p = data.shape[1]
#     s = np.cov(x.T)
#     w = np.eye(p)
#     r = 0
#     converged = False
#     w_current = w
#     # print T(0,1, w, s, lam)
#     # print T_vector(w, s, lam)[:3,:3]
#     while not converged and r < maxit:
#         w_old = w_current
#         # Updates to covariances w_ij

#         for i in range(p):
#             for j in range(p):
#                 w_current[i, j] = t(i, j, w_current, s, lam)

#         # wr.append(w_current)
#         # check convergence
#         converged = np.amax(w_current - w_old) < tol
#         r += 1
#     if np.isnan(w_current[0, 0]):
#         from pdb import set_trace
#         set_trace()
#     return w_current


def row_diff(x):
    # MUST BE A FORTRAN ARRAY
    # see https://docs.scipy.org/doc/numpy/reference/generated/numpy.asfortranarray.html#numpy.asfortranarray
    n, p = x.shape
    d = np.zeros((n - 1, p))
    for i in range(p):
        d[:, i] = np.diff(x[:, i])

    return d


def concord_weights(returns, coef_mu=1):
    """Cross-validate to find the best penalty and then compute the
    weights

    Parameters
    ----------
    returns -- Matrix of returns
    """
    # compute returns

    lambda_min, lambda_1sd, mean_sparsity, std_sparsity, mean_rss, std_rss = cross_validate(returns)
    omega_hat = concord(returns, lambda_1sd).todense()
    vector = np.ones((omega_hat.shape[0], 1))
    coef = 1 / np.dot(np.dot(vector.T, omega_hat), vector)
    w_eff = float(coef) * np.dot(omega_hat, vector)

    if coef_mu == 1:
        pass
    else:
        # mu_returns = self.get_mean(prices)
        # mu_min = float(dot(mu_returns, w_min))
        # mu = mu_min * coef_mu  # Try 2 first
        # w_eff = get_w_eff(mu_returns, omega_hat, mu)
        pass
    return (w_eff, lambda_min, lambda_1sd, omega_hat, mean_sparsity, std_sparsity,
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


# def get_mean(prices, n_maf=4):
#     """Get the underlying mean of the returns by regressing the stock
#     prices on the first k mafs and then taking the differences of the
#     fit.

#     Parameters
#     ----------
#     prices : np.array, n-by-p of time series
#     n_maf : number of mafs to use in regression

#     Returns
#     -------
#     r_hat_mean : Estimated mean returns using the maf reduction
#     """
#     n, p = prices.shape
#     holding_period = 28
#     mafs, w = maf(prices)
#     mafs = mafs[:, :n_maf]
#     x = sm.add_constant(mafs)
#     d = np.dot(linalg.inv(np.dot(x.T, x)), x.T)
#     beta_hat = np.dot(d, prices)
#     p_hat = np.dot(x, beta_hat)

#     # regress linear trend on last days of period using mafsmooth as predictors
#     linear_trend = np.arange(n)
#     beg_ind = n - holding_period

#     data = {'y': p_hat[beg_ind:, :], 'x': linear_trend[beg_ind:]}
#     outcome, predictors = dmatrices("y ~ x", data)
#     betas = np.linalg.lstsq(predictors, outcome)[0]
#     r_hat = np.dot(predictors, betas)

#     # r = get_returns(prices)

#     # if debug:
#     #     if self.period == 0:
#     #         if not os.path.isdir('debug'):
#     #             os.makedirs('debug')
#     #     self.period += 1
#     #     fig, axs = plt.subplots(5,
#     #                             5,
#     #                             figsize=(15, 6),
#     #                             facecolor='w',
#     #                             edgecolor='k')
#     #     fig.subplots_adjust(hspace=.1, wspace=.01)
#     #     axs = axs.ravel()
#     #     for i, ax in enumerate(axs):
#     #         # ax.plot(prices[:, i], label="obs")
#     #         ax.plot(p_hat[:, i], label="mean")
#     #         ax.plot(prices[:, i], label="obs")
#     #         ax.plot(np.linspace(beg_ind, estimation_horizon, holding_period),
#     #                 r_hat[:, i],
#     #                 label="mean")
#     #         ax.set_xlim((0, estimation_horizon))
#     #     plt.savefig('debug/mean_period_%d.pdf' % self.period)
#     #     plt.close(fig)

#     return betas[1, :]s

# def maf_smooth(y, n_maf=2):
#     """Smooth matrix with time series in the columns according to the
#     first user-specified MAFs in the time series
#     """
#     mafs, w = maf(y)
#     mafs = mafs[:, :n_maf]
#     x = sm.add_constant(mafs)
#     d = np.dot(np.linalg.inv(np.dot(x.T, x)), x.T)
#     beta_hat = np.dot(d, y)
#     y_hat = np.dot(x, beta_hat)
#     return y_hat


# def get_omega(self, returns, lam):
#       p = returns.shape[1]
#       std = np.std(returns, axis=0)
#       d_inv = np.diag(1 / std)
#       r_sparse = concord(scale(returns), lam)
#       r_hat = r_sparse.todense()
#       omega = np.dot(np.dot(d_inv, r_hat), d_inv)
#       sparsity = 1 - (r_sparse.nnz - p) / float((p * (p-1)))
#       return (omega, sparsity)

# def get_omega(data, penalty):
#     """Get the inverse covariance given a penalty. The data is scaled
#     and the back-transformed to the original scale.
#     Sparsity is also returned of the resulting omega (inverse covariance).
#     """
#     p = data.shape[1]
#     # d = np.diag(std)
#     # d_inv = np.diag(1 / std)
#     # r_sparse = concord(scale(data), penalty)
#     r_sparse = concord(data, penalty)
#     r_hat = r_sparse.todense()
#     # sigma = dot(d, dot(linalg.inv(r_hat), d))
#     # omega = dot(dot(d_inv, r_hat), d_inv)
#     omega = np.array(r_hat)

#     sparsity = 1 - (r_sparse.nnz - p) / float((p * (p - 1)))
#     return (omega, sparsity)

if __name__ == '__main__':
    from test_main import mock_df
    prices = mock_df.loc[:'2009-09', :].to_numpy()
    returns = np.diff(prices, axis=0) / prices[:-1, :]
    concord_weights(np.array(returns))
