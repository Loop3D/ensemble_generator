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

#%% litho probabilities

def litho_probabilities(array):
    '''computes the probability of all lithologies at a given location'''
    t1_start = process_time()
    #litho_prob = pd.DataFrame(np.zeros([int(header.loc[6, 1] * header.loc[6, 2] * header.loc[6, 3]), len(np.unique(array))]))
    lithos = np.unique(array)
    lithos = lithos.astype(int)
    litho_prob = pd.DataFrame({'LithoID': lithos.astype(int)}) # dataframe to store results
    for r in range(len(array)):
        # loop through rows
        unique, counts = np.unique(array.loc[r], return_counts=True)
        #test = dict(zip(unique, counts))
        litho_prob[r] = litho_prob['LithoID'].map(dict(zip(unique, counts)))
    litho_prob = litho_prob/len(prop_files)
    t1_stop = process_time()
    print("Elapsed time:", t1_stop, t1_start)

    print("Elapsed time during the whole program in seconds:",
          t1_stop - t1_start)
    return(litho_prob)

#%%


