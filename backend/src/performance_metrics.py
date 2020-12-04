import numpy as np

days2year = 250


def short_size(weights):
    """The proportion of the negative weights to the sum of the
    absolute weights of each portfolio.
    """
    n_periods = len(weights)
    short_size = np.zeros(n_periods)

    for k in range(n_periods - 1):
        weights_k = weights[k]
        negative_weights = weights_k[weights_k < 0]
        if negative_weights.size == 0:
            short_size[k] = 0
        else:
            sumabs_weights = np.sum(np.abs(weights_k))
            short_size[k] = -np.sum(negative_weights) / sumabs_weights

    return short_size


def turnover(returns, times, rebalance_dates, n_periods, weights):
    """Compute turnover: The amount of new portfolio assets
    purchased or sold over each trading period.
    """
    t = times
    r1 = (returns + 1)
    rd = rebalance_dates
    p = weights.shape[1]

    turnover = np.zeros(n_periods)
    r1_prod = np.zeros(p)
    for k in range(n_periods):
        if k == 0:
            term = weights[k]
        else:
            if k == n_periods - 1:
                idx = t >= rd[k]
            else:
                idx = np.logical_and(t >= rd[k], t < rd[k + 1])

            r1_tr = r1[idx, :]
            for i in np.arange(p):
                r1_prod[i] = np.prod(r1_tr[:, i])
            term = weights[k] - r1_prod * weights[k - 1]

        turnover[k] = np.sum(np.abs(term))

    return turnover


def realized_values(weights,
                    returns,
                    times,
                    rebalance_dates,
                    riskfree_rate=0.05):
    """The workhorse for realized returns, risk and sharpe.
    Compute all of these at the same time to save computation
    time
    """
    n_periods = len(weights)
    r = returns
    t = times
    rd = rebalance_dates
    ret_mean = np.zeros(n_periods)
    ret_vec = np.zeros(len(t))
    ret_square = np.zeros(n_periods)

    for i in range(n_periods):

        if i == n_periods - 1:
            idx = t >= rd[i]
        else:
            idx = np.logical_and(t >= rd[i], t < rd[i + 1])
        r_tr = r[idx, :]

        rwts = np.dot(r_tr, weights[i])

        ret_mean[i] = np.mean(rwts)
        ret_square[i] = np.sum(np.power(rwts, 2)) / len(rwts)

        ret_vec[idx] = rwts

    realized_return = np.mean(ret_mean)
    realized_risk = np.sqrt(np.mean(ret_square) - realized_return**2)
    realized_return_vector = ret_vec
    sharpe = (realized_return - riskfree_rate) / realized_return

    return realized_return, realized_risk, realized_return_vector, sharpe


def wealth_growth(returns,
                  times,
                  rebalance_dates,
                  realized_return_vector,
                  weights):
    """Normalized wealth growth: Accumulated wealth derived from the
    portfolio over the trading period when the initial budget is
    normalized to one. Note that both transaction costs and borrowing
    costs are taken into account.
    """
    borrowing_rate = 0.07
    transaction_cost_rate = 0.005
    borrowing_daily_rate = borrowing_rate / 250  # Adjust from annual to daily
    n_periods = len(weights)
    n_holding_days = np.diff(
        rebalance_dates.astype('datetime64[D]')).astype(int)
    borrowing_cost = np.zeros(n_periods)
    investing_start_date = rebalance_dates[0].astype(
        'datetime64[D]')  # first inverstment
    invst_bool = investing_start_date <= times
    investment_times = times[invst_bool]
    n_investement_timesteps = len(investment_times)
    wealth_growth = np.zeros(n_investement_timesteps)

    # Get borrowing costs
    for k in range(n_periods):
        if k == 0:
            borrowing_cost[k] = 0
        else:
            weights_lastk = weights[k - 1]
            negative_weights = weights_lastk[weights_lastk < 0]
            coef = np.power(1 + borrowing_daily_rate,
                            n_holding_days[k - 1]) - 1

            if negative_weights.size == 0:
                borrowing_cost[k] = 0
            else:
                borrowing_cost[k] = -coef * np.sum(negative_weights)

    # Get transaction costs
    transaction_cost = transaction_cost_rate * turnover(
        returns[invst_bool, :], investment_times, rebalance_dates, n_periods, weights)

    gain = 1 + realized_return_vector

    period = 0

    for t, day in enumerate(investment_times):
        is_trading_day = np.any(np.isin(day, rebalance_dates))
        if is_trading_day:

            gain[t - 1] -= (transaction_cost[period] + borrowing_cost[period])

            period += 1
        if t == 0:
            wealth_growth[t] = 1
        else:
            wealth_growth[t] = wealth_growth[t - 1] * gain[t - 1]

    return wealth_growth, investment_times.astype(str)
