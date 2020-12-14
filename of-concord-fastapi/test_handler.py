import handler
import numpy as np

returns = np.array(
    [
        [0.00574713, -0.00888889],
        [0.01142857, -0.00896861],
        [-0.0094162, -0.01131222],
        [-0.01901141, -0.01372998],
        [-0.01550388, 0.01856148],
        [-0.0019685, 0.00455581],
        [-0.00788955, 0.01587302],
        [0.00397614, 0.00446429],
        [-0.02178218, 0.0],
        [0.00404858, 0.00444444],
    ]
)


def test_handle():
    weights, optimal_lambda = handler.robust_concord_weights(returns)
    assert np.all(weights > 0)
