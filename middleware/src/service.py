import pandas as pd
import numpy as np
import helper


def get_portfolio(tickers, method):

    prices = helper.get_data(tickers)
    weights, returns, times, rebalance_dates = helper.get_weights(prices, method=method)
    wealth_times, wealth_values = helper.get_wealth(weights, returns, times, rebalance_dates)

    result_ts = pd.DataFrame(
        data=np.array([np.around(wealth_values, 3), wealth_times]).T,
        columns=['value', 'date'])
    weights_data = [{'value': w, 'date': rbd} for w, rbd in zip(weights.tolist(), rebalance_dates.astype(str).tolist())]
    result = {
        'wealth_data': result_ts.to_json(orient='records'),
        'weights_data': weights_data
    }

    return result
