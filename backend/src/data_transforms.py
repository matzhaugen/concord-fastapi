import numpy as np
from numpy import dot
import pandas as pd
import time
from performance_metrics import wealth_growth, realized_values
import requests

debug = False

BACKEND_URL = "http://backend:80"

def get_wealth(weights, returns, times, rebalance_dates):
    realized_return, realized_risk, realized_return_vector, sharpe = \
        realized_values(weights, returns, times, rebalance_dates)

    wealth_values, wealth_times = wealth_growth(returns, times, rebalance_dates,
                                                realized_return_vector, weights)
    return wealth_times, wealth_values
