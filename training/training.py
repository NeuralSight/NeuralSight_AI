import yaml
import os
import pandas as pd
import numpy as np
from glob import glob


os.system("pip install  -U wandb -q")
import wandb

import dotenv
dotenv.load_dotenv()


WANDB_API_KEY = os.getenv("WANDB_API_KEY")
TRAIN_DIR = os.getenv("TRAIN_DIR")

# # set key variabkes
os.environ["WANDB_API_KEY"] = WANDB_API_KEY
os.environ["WANDB_MODE"] = "online"


wandb.login()

wandb.init(project="VinBig", entity="nueurallabs")


classes = {'Cardiomegaly': 3,
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
 'Pneumothorax': 12}



# we use coco format.
CURR_DIR = os.getenv("CURR_DIR")
with open(os.path.join( CURR_DIR , 'train.txt'), 'w') as f:
    for path in glob(f'{TRAIN_DIR}/images/train/*'):
        f.write(path+'\n')
        
with open(os.path.join( CURR_DIR , 'val.txt'), 'w') as f:
    for path in glob(f'{TRAIN_DIR}/images/val/*'):
        f.write(path+'\n')
        
# data infromation

data = dict(
    train =  os.path.join( CURR_DIR , 'train.txt') ,
    val   =  os.path.join( CURR_DIR, 'val.txt' ),
    nc    = len(classes),#we hgave x classes
    names = [k for k,v in classes.items()]
    )
print("Data Config:  " ,data)

# create yaml file with information of the above two files


with open(os.path.join( CURR_DIR , 'custom.yaml'), 'w') as outfile:
    yaml.dump(data, outfile, default_flow_style=False)
    
    
# clone the repo
# https://www.kaggle.com/ultralytics/yolov5

os.system("git clone https://github.com/ultralytics/yolov5")
os.system("cd yolov5")



os.chdir(f'{CURR_DIR}/yolov5')
os.system("pip install -qr requirements.txt") # install dependencies



import torch
from IPython.display import Image, clear_output  # to display images

clear_output()
print('Using torch %s %s' % (torch.__version__, torch.cuda.get_device_properties(0) if torch.cuda.is_available() else 'CPU'))

data_config_path = "/kaggle/working/custom.yaml"
os.system("python train.py --img 640 --batch 8 --epochs 25 --data /kaggle/working/custom.yaml --weights yolov5x.pt")
