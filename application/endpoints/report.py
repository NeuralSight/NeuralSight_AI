from datetime import timedelta
from typing import Any, List
from core import security
from fastapi import APIRouter, Body, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from core.config import settings
from endpoints import deps
from helpers import get_random_string



import crud, model as models, schemas
import os, shutil, io, cv2, torch
import pandas as pd
import numpy as np
from PIL import Image
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import random
from fastapi import FastAPI, File, Form, UploadFile
import string, time
import boto3, botocore, os

from helperApp import *
from datetime import datetime

# s3 config
load_dotenv()

# Model Loading
import wandb
run = wandb.init()
artifact = run.use_artifact('stephenkamau/YOLOv5/run_eoi3j9y3_model:v0', type='model')
artifact_dir = artifact.download()

artifact_dir = "./endpoints"
print("artifact Dir: ",artifact_dir, os.path.isfile("./endpoints/best.pt"))
#
# # load model
model = torch.hub.load('ultralytics/yolov5', 'custom', path=f"{artifact_dir}/best.pt", force_reload=True)





router = APIRouter()



@router.post("/")
async def create_patient(
user_id: str = Form(),
db: Session = Depends(deps.get_db),
current_user: models.User = Depends(deps.get_current_active_user)
):
    # #create patient table
    patient = crud.patient.create(db, obj_in={"id":user_id, "user_id":current_user.id, "created_at":datetime.now(), "updated_at":datetime.now()})

    return {"patient":patient, "status":"OK"}


# create report endpoint
@router.post('/predict')
async def upload_file(file: UploadFile,
patient_id: str= Form(),
db: Session = Depends(deps.get_db),
current_user: models.User = Depends(deps.get_current_active_user),
):

    # check if patient exists in the database...
    #upload the text file
    # checking if image uploaded is valid
    patient = crud.patient.get(db, id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="The Patient  with this Id does not exist in the system",
        )

    #end

    if file.filename == '':
        return {"message":"Missing file parameter!", "status":400}

    file_to_save =get_random_string(15, file.filename.split(".")[0])
    request_object_content = await file.read()
    # img_bytes = await file.read()
    uploaded_img = Image.open(io.BytesIO(request_object_content))

    results = model(uploaded_img, size=640)


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
    created_res = [[results.names.get(int(a), None) if item.index(a)==5 else a for a in item[-2:]] for item in results.pred[0].tolist()]
    txt_data = [" ".join(["".join(str(a)) for a in item ]) for item in created_res]
    txt_data = "\n".join(txt_data)
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


    # #update patient table

    annotation_path = '%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv("AWS_ANNOTATIONS_FOLDER") ,f"{file_to_save}.txt")
    inference_path = '%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv("AWS_INFERENCE_FOLDER") ,f"{file_to_save}.png")
    report = crud.report.create(db, obj_in={"id":file_to_save, "patient_id":patient_id,
    "inference_path":inference_path, "annotation_path":annotation_path, "created_at":datetime.now(), "updated_at":datetime.now()
    })
    # --

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
        },
        "Reports":report
        }}

    # return {"Org": "Neural Labs Africa", "status":"Ok", "message":"Successful Loaded!", "user_id":patient}




# get all patients
@router.get("/")
def get_all_patients(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve Patients.
    """
    patients = crud.patient.get_multi(db, skip=skip, limit=limit)
    print("Here")
    # response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    # response.headers["Content-Range"] = f"0-9/{len(patients)}"
    return patients



# get one patient with report
@router.get("/{patient_id}")
def read_patient_by_id(
    patient_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific patient by id.
    """
    patient = crud.patient.get(db, id=patient_id)

    return {"patient":patient, "patient report":patient.report}


@router.get("/report/{user_id}")
def read_docters_report(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific patient by id.
    """
    patients = crud.patient.get_by_user_id(db, user_id=current_user.id)

    return {"patients":patients}


# TODO : DELETE PATIENT/REPORT

@router.put("/report/update/{patient_id}")
def update_patient(
    *,
    db: Session = Depends(deps.get_db),
    report: str = Form(),
    patient_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    patient = crud.patient.get_by_field(db, field=patient_id)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="The Patient  with this Id does not exist in the system",
        )
    patient = crud.patient.update(db, db_obj=patient, obj_in={"report":report})
    return patient
