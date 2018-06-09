#!/usr/bin/env python
import pickle
import os.path

from xmlread import files, leer


if __name__ == '__main__':
    nodules = []
    for f in files:
        try:
            nodules.extend(leer(f))
        except:
            continue

    pickle.dump(nodules, open(os.path.join(
         'data',
         'nodule_segmentation_polygons.pkl'), 'wb'))
