import numpy as np
from main import robust_concord_weights

returns = np.random.randn(1000, 200)


def test_robust_concord_weights():
    weights, opt_lambda = robust_concord_weights(returns)
    assert np.sum(weights) > 0
