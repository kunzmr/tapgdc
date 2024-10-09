import pandas as pd
import numpy as np

def matrix2table(x:pd.DataFrame, pulse_iteration = 0):
    n = x.shape[0]
    p = x.shape[1]
    pulse_index = np.repeat(np.arange(p), n)
    time_index = np.tile(np.arange(n), p)
    out = pd.DataFrame({
        'time_index': time_index, 
        'pulse_index': pulse_index
        })
    out['pulse_iteration'] = pulse_iteration
    out['flux'] = x.T.to_numpy().flatten().round(5)
    out = out[['pulse_iteration', 'pulse_index', 'time_index', 'flux']]
    return out