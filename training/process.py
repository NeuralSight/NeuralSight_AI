
# import som modules

# import wandb
from tqdm.notebook import tqdm
from glob import glob
import shutil, os
import cv2
import pandas as pd
import numpy as np
from cleaning import create_data

# 



import warnings
warnings.filterwarnings("ignore");





DATA_DIR = "/kaggle/input/vinbigdata-512-image-dataset/vinbigdata"

# read the data
df = pd.read_csv(f'{DATA_DIR}/train.csv')

df1 = df[["image_id","x_min","y_min","x_max","y_max","class_id", "height", "width", "class_name"]].dropna()
df1['path'] = df1['image_id'].apply(lambda x: f"{DATA_DIR}/train/{x}.png")

# get class id
class_dict = {v:k for k,v in dict(df1[['class_name', "class_id"]].values).items()}


# save  df1 in order to use it for plotting
df1.to_csv("train_clean.csv", index=False)


check_df = create_data(df1)
# class names available
classes = list(check_df['class_name'].unique())




# Yolo normaly requires bbox to be normalized between 0 and 1.
# Since we have have height and width for a particular image, we gonna just divide bbox against either widht or height.
# We then extract the widht and height of the bbox from the above calibrations


df = check_df.copy()

df['x_min'] = df.apply(lambda x: (x.x_min)/x.width, axis =1)
df['y_min'] = df.apply(lambda x: (x.y_min)/x.height, axis =1)

df['x_max'] = df.apply(lambda x: (x.x_max)/x.width, axis =1)
df['y_max'] = df.apply(lambda x: (x.y_max)/x.height, axis =1)
df['x_mid'] = df.apply(lambda x: (x.x_max+x.x_min)/2, axis =1)
df['y_mid'] = df.apply(lambda x: (x.y_max+x.y_min)/2, axis =1)
df['w'] = df.apply(lambda x: (x.x_max-x.x_min), axis =1)
df['h'] = df.apply(lambda x: (x.y_max-x.y_min), axis =1)

df['area'] = df['w']*df['h']


selected_classes = (df['class_name'].value_counts(normalize=True).T[df['class_name'].value_counts(normalize=True).T >0.0001])
SELECTED_CLASS_NAMES  = list(selected_classes.index)

# Get a dataframe with selected classes
selected_df = df[df['class_name'].isin(SELECTED_CLASS_NAMES)]


# only which have below 40 bbox instances
img_ids = list((df['image_id'].value_counts(normalize=False).T[df['image_id'].value_counts(normalize=False).T <=40]).index)


# pd.DataFrame(base_details)

TRAIN =[]
# for img_id in selected_df['image_id'].unique():
for img_id in selected_df[selected_df['image_id'].isin(img_ids)]['image_id'].unique():
    curr_df = selected_df[selected_df['image_id'] ==img_id].reset_index(drop=True)
    base_details = dict(curr_df.loc[0][['image_id',"path",'width', 'height']])
    information =[]
    for indx in range(curr_df.shape[0]):
        other_details = dict(curr_df.loc[indx][['class_name', "x_min", "y_min","x_max","y_max", "x_mid", "y_mid", "w", "h", "area" ]])
        information.append(other_details)
    
    TRAIN.append([base_details['image_id'],base_details['path'] ,base_details['width'],base_details['height'],information])
    

final_data = pd.DataFrame(TRAIN, columns =['image_id',"path", "width", "height", "information"])
from pprint import pprint
print(final_data.head())
# save this data for feature usage.
final_data.to_csv("processed.csv", index=False)
