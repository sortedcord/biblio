# Remove unshortened links from ids
# # Open ids.dat with pickle

import pickle
import os
import sys

with open('ids.dat', 'rb') as f:
    ids = pickle.load(f)
z = ids.copy()
for id in z:
    if "drive" in ids[id]:
        del ids[id]

with open('ids.dat', 'wb') as f:
    pickle.dump(ids, f)