from math import log, e
import numpy as np
from time import process_time # remove this once functions are finished

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

#test_prob = np.random.randint(low = 1, high = 15, size = 100)
test_prob = litho_df.loc[1]

array = litho_df

def litho_probabilities(array):
    '''computes the probability of all lithologies at a given location'''
    litho_prob = pd.DataFrame(np.zeros([int(header.loc[6, 1] * header.loc[6, 2] * header.loc[6, 3]), len(np.unique(array))]))
    lithos = np.unique(array)
    lithos = lithos.astype(int)
    t1_start = process_time()
    for r in range(len(array)):
        # loop through rows
        for c in lithos:
            litho_prob.iloc[r,c] = np.count_nonzero(array.iloc[r] == c) / array.shape[1]

    t1_stop = process_time()
    print("Elapsed time:", t1_stop, t1_start)

    print("Elapsed time during the whole program in seconds:",
          t1_stop - t1_start)

    litho_prob_2 = pd.DataFrame(np.zeros([int(header.loc[6, 1] * header.loc[6, 2] * header.loc[6, 3]), len(np.unique(array))]), index=lithos.astype(str))

    lithos_2 = pd.DataFrame(np.zeros([16]), index=lithos.astype(str))
    lithos_2 = lithos_2.T
    test = litho_df.iloc[143454].value_counts()
    test = test.to_frame().T
    lithos_2.merge(test)
    litho_prob_2.merge(test)





