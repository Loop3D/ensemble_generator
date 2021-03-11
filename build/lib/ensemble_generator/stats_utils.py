from math import log, e
from time import process_time # remove this once functions are finished
import numpy as np
import pandas as pd

#%% Define some functions for statisical analysis on model ensembles

# information entropy - this assumes the inputs are labels, but also works with numerics

def entropy_custom(array, base=None):
  """ Computes entropy of label distribution. """

  n_labels = len(array)

  if n_labels <= 1:
    return 0

  value,counts = np.unique(array, return_counts=True)
  probs = counts / n_labels
  n_classes = np.count_nonzero(probs)

  if n_classes <= 1:
    return 0

  ent = 0.

  # Compute entropy
  base = e if base is None else base
  for i in probs:
    ent -= i * log(i, base)

  return ent

#%% calculate the probability (between 0 and 1) of a lithology in a cell

def litho_probabilites(array):
    lithos = np.unique(array)
    litho_prob = pd.DataFrame([])
    for i in range(0, int(lithos.max())+1):
        temp = array[array == i]
        temp_counts = temp.count(axis=1)
        litho_prob = litho_prob.append(temp_counts, ignore_index=True)
    litho_prob = litho_prob / array.shape[1]
    return(litho_prob)

#%%
# group splitter


def split(x, n):
    # If we cannot split the
    # number into exactly 'N' parts
    if (x < n):
        return -1

    # If x % n == 0 then the minimum
    # difference is 0 and all
    # numbers are x / n
    elif (x % n == 0):
        temp = np.zeros(n)
        for i in range(n):
            temp[i] = x // n
        return temp
    else:
        # upto n-(x % n) the values
        # will be x / n
        # after that the values
        # will be x / n + 1
        temp = np.zeros(n)
        zp = n - (x % n)
        pp = x // n
        for i in range(n):
            if (i >= zp):
                temp[i] = pp + 1
            else:
                temp[i] = pp

        return temp



