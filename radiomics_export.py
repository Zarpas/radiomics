from radiomics.featureextractor import RadiomicsFeaturesExtractor
import radiomics
import h5py
import matplotlib.pyplot as plt
from skimage import measure
import numpy as np
import pandas as pd
import SimpleITK as sitk
from pathlib import Path
from tqdm import tqdm
import sys


DATASET_FILE = "/mnt/Data/LUNA/dataset_1mm.hdf5"
ANNOTATIONS_FILE = "/mnt/Data/LUNA/CSVFILES/annotations.csv"
MASK_FILE_PREFIX = "/mnt/Data/LUNA/results/evaluation_nodule_segmentation_augmentation_normalization_bce_3ch_laplacian_f6c98ba/"

def dataset_to_sitk(arr, origin, spacing=(1.0, 1.0, 1.0)):
    img = sitk.GetImageFromArray(arr)
    img.SetSpacing(spacing)
    img.SetOrigin(origin)
    return img

def process_mask_file(mask_file, annotations_file, dataset_file):
    dataset = h5py.File(dataset_file, 'r')["ct_scans"]
    ann_df = pd.read_csv(annotations_file)
    ds_mask = h5py.File(mask_file, 'r')
    
    radiomics_extractor = RadiomicsFeaturesExtractor()
    radiomics_extractor.enableAllFeatures()
    radiomics_extractor.enableImageTypeByName("Original")
    
    nodule_features_list = []
    seriesuids = list(ds_mask.keys())
    for sid in tqdm(seriesuids):
        origin = dataset[sid].attrs["origin"]
        originX, originY, originZ = origin[0], origin[1], origin[2]
        nodule_labels = measure.label(ds_mask[sid].value)
        nodule_props = measure.regionprops(nodule_labels)
        num_nodules = len(np.unique(nodule_labels))
        if num_nodules <= 1:
            continue
        for idx, props in zip(range(1, num_nodules), nodule_props):
            # Trying to find a matching annotation so I know the mask is a real nodule or a false positive
            if (nodule_labels == idx).sum() == 0:
                continue
            is_match = False
            ann_view = ann_df[ann_df.seriesuid == sid]
            for _, row in ann_view.iterrows():
                distance = np.sqrt(
                    (row.coordX - props.centroid[2] - originX)**2 + 
                    (row.coordY - props.centroid[1] - originY)**2 + 
                    (row.coordZ - props.centroid[0] - originZ)**2
                )
                if distance <= (row.diameter_mm / 2):
                    is_match = True
                    break
            # Converting image to sitk
            img_scan = dataset_to_sitk(dataset[sid].value, origin, spacing=(1.0, 1.0, 1.0))
            img_mask = dataset_to_sitk(nodule_labels, origin, spacing=(1.0, 1.0, 1.0))
            # Extracting radiomics
            features = radiomics_extractor.execute(img_scan, img_mask, label=idx)
            image_features = {f: features[f] for f in features.keys() if "general_" not in f}
            # Add a few features to the file that will be saved as a DataFrame
            image_features["match"] = is_match
            image_features["seriesuid"] = sid
            image_features["subset"] = dataset[sid].attrs["subset"]
            image_features["centroid"] = props.centroid
            nodule_features_list.append(image_features)
    return nodule_features_list

mask_file = MASK_FILE_PREFIX + sys.argv[1]
features = process_mask_file(mask_file, ANNOTATIONS_FILE, DATASET_FILE)

df = pd.DataFrame(features)
df = df.dropna()
df.to_csv("/home/ofont/radiomics/data/" + sys.argv[2])
