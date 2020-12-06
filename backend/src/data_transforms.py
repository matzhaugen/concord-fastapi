from src.performance_metrics import realized_values, wealth_growth

debug = False

BACKEND_URL = "http://backend:80"


def get_wealth(weights, returns, times, rebalance_dates):
    realized_return, realized_risk, realized_return_vector, sharpe = realized_values(
        weights, returns, times, rebalance_dates
    )

    wealth_values, wealth_times = wealth_growth(returns, times, rebalance_dates, realized_return_vector, weights)
    return wealth_times, wealth_values
