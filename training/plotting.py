
import numpy as np
import pandas as pd
import os, shutil
import seaborn as sns
import matplotlib.pyplot as plt
import cv2 
import torch


# draw sample images


# draw sample images

def draw_single_img(df, img_id):
    
    bb_df = df[df.image_id == img_id].reset_index(drop =True)
    if bb_df.shape[0]==0:
        return "No Image With Such ID found"
    file_path = bb_df.iloc[0]['path']
    BB_IMG = cv2.imread(f"{file_path}")
    new_bb_img = cv2.resize(BB_IMG, (bb_df.iloc[0]['width'],bb_df.iloc[0]['height']))

    color = (255,0,0)
    for i in range(bb_df.shape[0]):
        row = bb_df.iloc[i]
        pt1 = int(row["x_min"]), int(row["y_min"])
        pt2 = int(row["x_max"]), int(row["y_max"])
        #height, width = row['height'], row['width']
        label = row["class_name"]
        ((text_width, text_height), _) = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1) 
        new_bb_img = cv2.rectangle(new_bb_img.copy(), pt1, pt2, color, int(max(new_bb_img.shape[:2]) / 500))
        #print(class_name)
        new_bb_img = cv2.putText(new_bb_img.copy(), label, (int(row["x_min"])+100, int(row["y_min"])), cv2.FONT_HERSHEY_SIMPLEX,fontScale=2,color = (255,0,255), lineType=cv2.LINE_AA)

    plt.figure(figsize=(13,13))
    plt.imshow(new_bb_img)
    

# lets plot multiple
def plot_multiple_img(img_matrix_list, title_list, ncols, main_title=""):
    fig, myaxes = plt.subplots(figsize=(25, 20), nrows=3, ncols=ncols, squeeze=False)
    fig.suptitle(main_title, fontsize = 30)
    fig.subplots_adjust(wspace=0.3)
    fig.subplots_adjust(hspace=0.3)
    for i, (img, title) in enumerate(zip(img_matrix_list, title_list)):
        myaxes[i // ncols][i % ncols].imshow(img)
        myaxes[i // ncols][i % ncols].set_title(title, fontsize=9)
    plt.show()
    

def draw_rect_with_labels(img, bboxes,class_id, class_dict, color=None):
    img = img.copy()
    bboxes = bboxes[:, :5]
    bboxes = bboxes.reshape(-1, 5)
    for bbox in bboxes:
        pt1, pt2 = (bbox[0], bbox[1]), (bbox[2], bbox[3])
        pt1 = int(pt1[0]), int(pt1[1])
        pt2 = int(pt2[0]), int(pt2[1])
        label = int(bbox[4])
        class_name = class_dict[label]
        ((text_width, text_height), _) = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.15, 1) 
        img = cv2.rectangle(img.copy(), pt1, pt2, color, int(max(img.shape[:2]) / 200))
        #print(class_name)
        img = cv2.putText(img.copy(), class_name, (int(bbox[0]), int(bbox[1]) - int(0.3 * text_height)), cv2.FONT_HERSHEY_SIMPLEX,fontScale=1,color = (255,255,255), lineType=cv2.LINE_AA)

    return img


def random_bbox_check(data, num = 12):
    img_dict = {}
    
    #skip_csv_header(file)
    counter =0
    for idx in range(data.shape[0]):
        row = data.iloc[idx]
        try:
            image_name, x_min, y_min, x_max, y_max, class_idx, h,w = (
                row['path'], 
                row['x_min'], row['y_min'],
                row['x_max'],row['y_max'], 
                row['class_id'],
                row['height'], row['width']
            )
            if image_name not in img_dict:
                img_dict[image_name] = list()
            img_dict[image_name].append(
                [float(x_min), float(y_min), float(x_max), float(y_max), int(class_idx), int(h), int(w)]
            )

        except ValueError:
            print("Could not convert float to string, likely that your data has empty values.")

    # randomly choose 12 image.
    img_files_list = np.random.choice(list(img_dict.keys()), num)
    print("The images' names are {}".format(img_files_list))
    image_file_path_list = []

    bbox_list = []
    img_matrix_list = []
    random_image_matrix_list = []
    class_ids =[]
    
    for img_file in img_files_list:
        image_file_path = os.path.join(img_file)
        img = cv2.imread(image_file_path)[:,:,::-1]
        #print(img.shape)
        img = cv2.resize(img, (img_dict[img_file][0][-2], img_dict[img_file][0][-1]))
        height, width, channels = img.shape
        bbox_list.append(img_dict[img_file])
        #print(img_dict[img_file])
        img_matrix_list.append(img)

    
    final_bbox_list = []
    for bboxes, img in zip(bbox_list, img_matrix_list):
        final_bbox_array = np.array([])
        #print(bboxes)
        #bboxes is a 2d array [[...], [...]]
        for bbox in bboxes:
            bbox = np.array(bbox).reshape(1,7)
            final_bbox_array = np.append(final_bbox_array, bbox)
        final_bbox_array = final_bbox_array.reshape(-1,7)
        random_image = draw_rect_with_labels(img.copy(), final_bbox_array.copy(),1,class_dict,  color = (255,0,0))
        random_image_matrix_list.append(random_image)
    plot_multiple_img(random_image_matrix_list, title_list = img_files_list, ncols = 4, main_title="Bounding Box Pathologies Images")    

    
