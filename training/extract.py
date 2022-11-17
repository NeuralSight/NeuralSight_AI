
import numpy as np
import os, shutil
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GroupKFold
import yaml
from tqdm import tqdm_notebook, tqdm, notebook




import dotenv
dotenv.load_dotenv()

DATA_DIR = os.getenv("DATA_DIRECTORY")
TRAIN_DIR = os.getenv("TRAIN_DIR")



BASE_IMG_TRAIN_DIR = f"{DATA_DIR}/train"


if not os.path.isfile("processed.csv"):
    print("Please Run the Process.py file Before running this script")
    exit(0)
# read the data
final_data = pd.read_csv("processed.csv")

# split the data
gkf  = GroupKFold(n_splits = 5)
final_data['fold'] = -1
for fold, (train_idx, val_idx) in enumerate(gkf.split(final_data, groups = final_data.image_id.tolist())):
    final_data.loc[val_idx, 'fold'] = fold

    
    
final_classes = {
        'Cardiomegaly': 3,
        'Aortic enlargement': 0,
        'Pleural thickening': 11,
        'ILD': 5,
        'Nodule/Mass': 8,
        'Pulmonary fibrosis': 13,
        'Lung Opacity': 7,
        'Atelectasis': 1,
        'Other lesion': 9,
        'Infiltration': 6,
        'Pleural effusion': 10,
        'Calcification': 2,
        'Consolidation': 4,
        'Pneumothorax': 12
                }
def get_class_id(class_value):    
    #print(class_value)
    return final_classes.get(class_value)


# get all image ids for both training and validation with the bbox

train_fold_files_ids = []
val_fold_files_ids   = []
val_fold_files_ids += list(final_data[final_data.fold==fold].image_id.unique())
train_fold_files_ids += list(final_data[final_data.fold!=fold].image_id.unique())




# shutil.rmtree(f'{TRAIN_DIR}/labels/train')
# shutil.rmtree(f'{TRAIN_DIR}/labels/val')
# shutil.rmtree(f'{TRAIN_DIR}/images/train')
# shutil.rmtree(f'{TRAIN_DIR}/images/val')

# create thr directorues
os.makedirs(f'{TRAIN_DIR}/labels/train', exist_ok = True)
os.makedirs(f'{TRAIN_DIR}/labels/val', exist_ok = True)
os.makedirs(f'{TRAIN_DIR}/images/train', exist_ok = True)
os.makedirs(f'{TRAIN_DIR}/images/val', exist_ok = True)




# create a data for processing
indexed_final_data = final_data.copy()
indexed_final_data.index = final_data['image_id']

"""
In this cell, It is a function that iterates through each row in the df
It first determine whether the image belows to training or testing sets.

 For each image:
    1- get the info for each bounding box
    2- write the bounding box info to a txt file
    3- save the txt file in the correct folder
    4- copy the image to the correct folder

Before saving the image, it must be processed by applying clahe function/
class, center (x,y), width, height

Also the format for YOLO dataset is followed i.e
"""

def process_data_for_yolo(df, file_id_lists, data_type='train'):
    """
    Reads details for an image and transfers them to their respective folders when proceesed.
    """
    #iterate through each row
    #for _, row in notebook.tqdm(df.iterrows(), total=len(df)):
    for each_id in notebook.tqdm(file_id_lists, total=len(file_id_lists)):
        #print(each_id, file_id_lists)
        row = df.loc[each_id]
        
        #print(eval(row['information']))
        
        #get img information
        file_id = row['image_id']
        # Convert into the Yolo input format
        yolo_data = []
        for xq in  eval(row['information']):
            curr_bbox_infor = [get_class_id(xq['class_name']), xq['x_mid'], xq['y_mid'], xq['w'] , xq['h']]
            yolo_data.append(curr_bbox_infor)

        # convert to nump array
        yolo_data = np.array(yolo_data)
        #print(yolo_data)
        #copy image to another directory where training will occur
        full_file_path = f"{BASE_IMG_TRAIN_DIR}/{file_id}.png"
        shutil.copy(full_file_path, f'{TRAIN_DIR}/images/{data_type}')
        
        #saved format must be class, center (x,y), width, heihgt 
        np.savetxt(os.path.join(f'{TRAIN_DIR}', 
                                f"labels/{data_type}/{file_id}.txt"),
                                yolo_data, 
                                fmt=["%d", "%f", "%f", "%f", "%f"]
                   )
        
        
print("INFO: Started Transferring Training Images and Labels")

# process training
process_data_for_yolo(indexed_final_data, train_fold_files_ids, 'train')

print("INFO: Started Transferring Testing Images and Labels")
# process testing
process_data_for_yolo(indexed_final_data, val_fold_files_ids, 'val')

