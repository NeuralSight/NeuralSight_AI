import sys
import os, shutil, io
from dotenv import load_dotenv
import random
import string, time

# s3 config
load_dotenv()
import boto3, botocore, os
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


# # function to uploads
# def writeData(yolo_object):
#     file_name = "curr"
#     txt_data = "\n".join([" ".join(["".join(str(a)) for a in item]) for item in yolo_object.pred[0].tolist()])
#     res_img = np.squeeze(yolo_object.ims)
#
#     file_object = s3.Object(f"{BUCKET_NAME}", f"{curr}.txt")
#     file_object.put(Body = txt_data)
#     return txt_data, res_img


def get_random_string(length, file_name):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    time_string = time.strftime("%Y%m%d%H%M%S")

    return str(file_name).replace(" ", "")+"_"+time_string +"_"+result_str
