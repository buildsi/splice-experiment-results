import sys
import os
import numpy as np
sys.path.insert(0, os.getcwd())
from helpers import recursive_find, create_fedora_results_table

try:
  import pandas
  df = pandas.read_pickle('dump.pickle')
except:
  experiments = list(recursive_find("artifacts/results/extracted/fedora", "*.json"))
  df = create_fedora_results_table(experiments)
  df.to_pickle('dump.pickle')


data = {
  'missing-previously-found-exports':
    {
      'size': df[df['analysis']=='missing-previously-found-exports']['size_original'].to_numpy(dtype=np.float64) +
              df[df['analysis']=='missing-previously-found-exports']['size_changed'].to_numpy(dtype=np.float64),
      'time': df[df['analysis']=='missing-previously-found-exports']['seconds'].to_numpy(dtype=np.float64)
    },
  'missing-previously-found-symbols':
    {
      'size': df[df['analysis']=='missing-previously-found-symbols']['size_original'].to_numpy(dtype=np.float64) +
              df[df['analysis']=='missing-previously-found-symbols']['size_changed'].to_numpy(dtype=np.float64),
      'time': df[df['analysis']=='missing-previously-found-symbols']['seconds'].to_numpy(dtype=np.float64)
    },
  'abidiff':
    {
      'size': df[df['analysis']=='abidiff']['size_original'].to_numpy(dtype=np.float64) +
              df[df['analysis']=='abidiff']['size_changed'].to_numpy(dtype=np.float64),
      'time': df[df['analysis']=='abidiff']['seconds'].to_numpy(dtype=np.float64)
    },
  'abi-compliance-tester':
    {
      'size': df[df['analysis']=='abi-compliance-tester']['size_original'].to_numpy(dtype=np.float64) +
              df[df['analysis']=='abi-compliance-tester']['size_changed'].to_numpy(dtype=np.float64),
      'time': df[df['analysis']=='abi-compliance-tester']['seconds'].to_numpy(dtype=np.float64)
    }
}

import scipy.stats
import scipy.signal
import matplotlib.pyplot as plt
import numpy as np

plt.figure()

for p in data.keys():
  indices = data[p]['size'] >= 1e7
  x = scipy.signal.medfilt(data[p]['size'][indices], kernel_size=11) 
  y = data[p]['time'][indices]
  y_binned, x_binned, _ = scipy.stats.binned_statistic(x, y, bins=50, statistic='mean')
  x_plot = x_binned[0:-1] + (x_binned[1:]-x_binned[0:-1])/2.0
  plt.scatter(np.log10(x_plot), np.log10(y_binned), label=p)

plt.xlabel(r"$log_{10}(\rm{size/MB})$")
plt.ylabel(r"$log_{10}(\rm{time/second})$")
plt.legend()
plt.savefig('timings.png')
