
import uvicorn
import os, shutil, io, cv2, torch
import pandas as pd
import numpy as np
from PIL import Image
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import random
from fastapi import FastAPI, File, Form, UploadFile
import string, time
import boto3, botocore, os

from helperApp import *

# s3 config
load_dotenv()

# Model Loading
import wandb
run = wandb.init()
artifact = run.use_artifact('stephenkamau/YOLOv5/run_eoi3j9y3_model:v0', type='model')
artifact_dir = artifact.download()

print("artifact Dir: ",artifact_dir)
#
# # load model
model = torch.hub.load('ultralytics/yolov5', 'custom', path=f"{artifact_dir}/best.pt", force_reload=True)



# app = Flask(__name__)
app = FastAPI()



# import logging
#
# from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
#
# from db.database import SessionLocal
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# max_tries = 60 * 1  # 1 minutes
# wait_seconds = 1
#
# from db.init_db import init_db
#
# def init() -> None:
#     db = SessionLocal()
#     init_db(db)
#
#
# def maininit() -> None:
#     logger.info("Creating initial data")
#     init()
#     logger.info("Initial data created")
#
#
# @retry(
#     stop=stop_after_attempt(max_tries),
#     wait=wait_fixed(wait_seconds),
#     before=before_log(logger, logging.INFO),
#     after=after_log(logger, logging.WARN),
# )
# def init() -> None:
#     try:
#         db = SessionLocal()
#         # Try to create session to check if DB is awake
#         db.execute("SELECT 1")
#     except Exception as e:
#         logger.error(e)
#         raise e
#
#
# def main() -> None:
#     logger.info("Initializing service")
#     init()
#     logger.info("Service finished initializing")
#
# print("Running Database Initialization")
# main()
# print("Creating super User")
# maininit()


@app.get("/")
def home():
    return {"Org": "Neural Labs Africa", "status":"Ok", "message":"Successful Loaded!"}


@app.post('/')
async def upload_file(file: UploadFile):
    #upload the text file
    # checking if image uploaded is valid

    if file.filename == '':
        return {"message":"Missing file parameter!", "status":400}

    file_to_save =get_random_string(15, file.filename.split(".")[0])
    request_object_content = await file.read()
    # img_bytes = await file.read()
    uploaded_img = Image.open(io.BytesIO(request_object_content))

    results = model(uploaded_img, size=640)

    #choice of the model
    print(f'User selected model : Yolo Best')
    # results = get_prediction(img_bytes,model)

    # updates results.ims with boxes and labels
    # encoding the resulting image and return it to s3.

    annotations_image = []
    results.render()
    for img in results.ims:
        RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        data_serial = cv2.imencode('.png', RGB_img)[1].tobytes()
        #save the annotated image and return the url
        annotated_name = s3.put_object(
            Body = data_serial,
            Bucket=f"{os.getenv('AWS_BUCKET_NAME')}",
            Key='%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv('AWS_INFERENCE_FOLDER'),f"{file_to_save}.png")
        )
        print("Uploaded Annotations")

        #append the name
        annotations_image.append(annotated_name)
    txt_data = "\n".join([" ".join(["".join(str(a)) for a in item]) for item in results.pred[0].tolist()])
    with open("filer.txt", "w") as dat:
        dat.write(txt_data)
        dat.close()
    annotations_urls = s3.upload_fileobj(
        open("./filer.txt", "rb"),
        os.getenv("AWS_BUCKET_NAME"), '%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv('AWS_ANNOTATIONS_FOLDER'),f"{file_to_save}.txt")
    )
    os.remove("filer.txt")
    # send the data to aws_secret_access_key
    filename = secure_filename(file.filename)
    # send file that was uploaded.
    #output_url = uploadFile(file, f"{file_to_save}.png", file.content_type)

    # print(f"{os.getenv('AWS_BUCKET_FOLDER')}")
    # s3.upload_fileobj(uploaded_img, f"{os.getenv('AWS_BUCKET_NAME')}",
    # '%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv('AWS_IMGS_FOLDER'),f"{file_to_save}.png"))
    # s3.put_object(
    #     Body = cv2.imencode('.png', cv2.cvtColor(uplp, cv2.COLOR_BGR2RGB))[1].tobytes(),
    #     Bucket=f"{os.getenv('AWS_BUCKET_NAME')}",
    #     Key='%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv('AWS_IMGS_FOLDER'),f"{file_to_save}.png")
    # )



    # write your code here
    # to save the file name in database
    return {"message":"Uploaded fille Successful!", "status":200, "results":{
        "annotations":{
            "Status":"Done",
            "URL": '%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv("AWS_ANNOTATIONS_FOLDER") ,f"{file_to_save}.txt")
        },
        "uploaded":{
            "Status":"Not Done",
            "URL": '%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv("AWS_IMGS_FOLDER") ,f"{file_to_save}.txt")
        },
        "annotations_image":{
            "Status":"DOne",
            "URL":'%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv("AWS_INFERENCE_FOLDER") ,f"{file_to_save}.png")
        }
        }}

    # return your image with boxes and labels
    return response
#

if __name__ == "__main__":
    uvicorn.run("hello_world_fastapi:app")
