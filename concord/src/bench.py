import concord_helper
import numpy as np
from test_main import mock_df

if __name__ == '__main__':

    prices = mock_df.loc[:'2009-09', :].to_numpy()
    returns = np.diff(prices, axis=0) / prices[:-1, :]
    concord_helper.concord_weights(np.array(returns))
