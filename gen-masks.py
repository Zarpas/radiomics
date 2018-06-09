#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy
import pickle
import h5py
import os.path
from skimage.measure import label, regionprops

from skimage.draw import polygon


def process_nodule(dataset, nodule):
    if nodule['UID'] not in list(dataset['ct_scans'].keys()):
        # print('UID not in dataset: ' + nodule['UID'])
        return
    # else:
    #     print('UID is in dataset: ' + nodule['UID'])

    originZ = int(round(dataset['ct_scans'][nodule['UID']].attrs['origin'][2]))
    shape = dataset['ct_scans'][nodule['UID']].shape
    shapeX, shapeY, shapeZ = shape[2], shape[1], shape[0]

    # zs = []

    # Ratios para convertir entre sistemas de coordenadas
    ratioX = float(shapeX) / 512.0
    ratioY = float(shapeY) / 512.0

    # slices = []

    imgt = numpy.zeros((shapeX, shapeY), dtype=numpy.double)
    for (z, rois) in nodule['rois'].items():
        # zs.append(float(z) - originZ)
        print("Z: %f" % (float(z) - originZ))
        zval = float(z) - originZ

        # print("z: " + str(z))
        # continue
        img = numpy.zeros((shapeX, shapeY), dtype=numpy.double)
        for roi in rois:
            coords = numpy.array(roi['coords'])
            if roi['inclusion']:
                value = 1
            else:
                value = 0
            # Ignore anotations of 1 pixel
            if len(coords) > 1:
                rr, cc = polygon(coords[:, 0] * ratioX,
                                 coords[:, 1] * ratioY,
                                 img.shape)
                img[rr, cc] = value
                # print(img)
                # slices[zval] = img
            else:
                return

        imgt += img
    fig, ax1 = plt.subplots(ncols=1, nrows=1, figsize=(10, 6))
    labels = label(imgt)
    prop = regionprops(labels)[0]
    #print(numpy.max(imgt))

    # x_min, y_min, x_max, y_max = prop.bbox
    # print(prop.bbox)
    # ax1.imshow(imgt[x_min-2:x_max+10, y_min-2:y_max+10], cmap='gray')
    # plt.show()

    # zmin = min(zs)
    # zmax = max(zs)
    # print("S: %d / %d / %d  - O: %d / %d / %d  - Min: %d / %d / %f - Max %d / %d / %f" % (
    #    shapeX, shapeY, shapeZ,
    #    originX, originY, originZ,
    #    xmin, ymin, zmin,
    #    xmax, ymax, zmax
    #    ))
    # print("X: S: %d / O: %d / %d / %d" % (shapeX, originX, xmin, xmax))
    # print("Y: S: %d / O: %d / %d / %d" % (shapeY, originY, ymin, ymax))
    # print("Z: S: %d / O: %d / %f / %f" % (shapeZ, originZ, zmin, zmax))
          

def process_nodules(dataset, nodules):
    for nodule in nodules:
        process_nodule(dataset, nodule)


def main():
    # print(list(dataset.keys()))
    # seriesuids = list(dataset['ct_scans'].keys())
    # print(list(seriesuids))
    nodules = pickle.load(open(os.path.join(
        'data',
        'nodule_segmentation_polygons.pkl'), 'rb'))
    print(nodules[0])

    dataset = h5py.File(os.path.join('data', 'dataset_1mm.hdf5'), 'r')

    print(len(nodules))

    process_nodules(dataset, nodules)


if __name__ == '__main__':
    main()
