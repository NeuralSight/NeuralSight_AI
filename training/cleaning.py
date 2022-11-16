


import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
import torchvision.ops.boxes as bops
# box1 = torch.tensor([[1213, 298, 1634, 537]], dtype=torch.float)
# box2 = torch.tensor([[1004, 782, 1880, 1824]], dtype=torch.float)
# iou = bops.box_iou(box1, box2)
# # tensor([[0.1382]])

def find_iou_intersection_value(box1, box2):
    box1 = torch.tensor([box1], dtype=torch.float)
    box2 = torch.tensor([box2], dtype=torch.float)
    return bops.box_iou(box1, box2)[0][0].item()




def get_class_Annotations(image_id, df):
    # get the 
    sample_df = df[df.image_id ==image_id]
    curr_data = {}
    for indx in sample_df.index:
        row = sample_df.loc[indx]
        bbox = [row.x_min, row.y_min, row.x_max, row.y_max]
        if row.class_name in curr_data:
            curr_data[row.class_name].append(bbox)
        else:
            curr_data[row.class_name] = [bbox]
            
    return curr_data



def NMS(boxes, overlapThresh = 0.1):
    #return an empty list, if no boxes given
    if len(boxes) == 0:
        return []
    x1 = boxes[:, 0]  # x coordinate of the top-left corner
    y1 = boxes[:, 1]  # y coordinate of the top-left corner
    x2 = boxes[:, 2]  # x coordinate of the bottom-right corner
    y2 = boxes[:, 3]  # y coordinate of the bottom-right corner
    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    areas = (x2 - x1 + 1) * (y2 - y1 + 1) # We have a least a box of one pixel, therefore the +1
    indices = np.arange(len(x1))
    for i,box in enumerate(boxes):
        temp_indices = indices[indices!=i]
        xx1 = np.maximum(box[0], boxes[temp_indices,0])
        yy1 = np.maximum(box[1], boxes[temp_indices,1])
        xx2 = np.minimum(box[2], boxes[temp_indices,2])
        yy2 = np.minimum(box[3], boxes[temp_indices,3])
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        # compute the ratio of overlap
        overlap = (w * h) / areas[temp_indices]
        if np.any(overlap) > overlapThresh:
            indices = indices[indices != i]
    return boxes[indices].astype(int)



def create_data(df):
    new_data =[]
    for each_img_id in df.image_id.unique():
        curr_data = get_class_Annotations(each_img_id, df)
        row = df[df.image_id ==each_img_id].reset_index(drop=True).iloc[0]
        for it in curr_data:
            curr_record = NMS(np.array(curr_data[f"{it}"]), 0.1)
            for val in curr_record:
                a,b,c,d = val
                new_data.append([f"{each_img_id}", f"{it}", a,b,c,d,row.width, row.height, row.path])
    return pd.DataFrame(new_data, columns=["image_id","class_name", 'x_min', 'y_min', 'x_max', 'y_max', "width", "height", 'path'])

