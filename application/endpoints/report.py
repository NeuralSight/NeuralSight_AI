# general imports...
from datetime import timedelta, datetime
from typing import Any, List

# External Libraries
import os, shutil, io, random
import cv2, torch
import pandas as pd, numpy as np
from PIL import Image
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import boto3, botocore
from io import BytesIO

# FastAPI and ORM
from fastapi import FastAPI, File, Form, UploadFile, APIRouter, Body, Depends, HTTPException, Response
from sqlalchemy.orm import Session

# Project's specific modules
from core import security
from core.config import settings
from endpoints import deps
from helpers import get_random_string
from helperApp import *
import crud, model as models, schemas
from fastapi.responses import StreamingResponse



# s3 config
load_dotenv()

# Model Loading
# import wandb
# run = wandb.init()
# artifact = run.use_artifact('stephenkamau/YOLOv5/run_eoi3j9y3_model:v0', type='model')
# artifact_dir = artifact.download()

artifact_dir = "./endpoints"
print("artifact Dir: ",artifact_dir, os.path.isfile("./endpoints/best.pt"))
#
# # load model
model = torch.hub.load('ultralytics/yolov5', 'custom', path=f"{artifact_dir}/best.pt", force_reload=True)





router = APIRouter()



@router.post("/")
async def create_patient(
patient_id: str = Form(),
db: Session = Depends(deps.get_db),
current_user: models.User = Depends(deps.get_current_active_user)
):
    #check if patient is available
    if crud.patient.get(db, id=patient_id):
        raise HTTPException(
                status_code=404,
                detail="The Patient  with this Id Already  exist in the system",
            )
    # #create patient table
    #print("USE ID ", current_user.id)
    #print("Created ID ", patient_id, "\n\n")
    try:
        patient = crud.patient.create(db, obj_in={"id":patient_id, "user_id":current_user.id, "created_at":datetime.now(), "updated_at":datetime.now()})
    except Exception as e:
        return {"message":f"An Error during Insertion i.e {e}!", "status":400}

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
            detail="The Patient  with this Id does not exist in the system Or maybe removed",
        )

    if patient.is_deleted:
        raise HTTPException(
            status_code=404,
            detail="The Patient  is already deleted",
        )
    #also check if the docktor that created the patient is the one updating
    if patient.user_id != current_user.id:
        print(patient.user_id, current_user.id)
        raise HTTPException(
            status_code=404,
            detail="Un Authorised Access to entry you did'nt Author",
        )
    #end

    if file.filename == '':
        return {"message":"Missing file parameter!", "status":400}

    file_to_save =get_random_string(5, patient.user_id)
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

    #base Path
    #'http://{}.s3.amazonaws.com/'.format(os.getenv("AWS_ANNOTATIONS_FOLDER"))

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
    #print("Here")
    # response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    # response.headers["Content-Range"] = f"0-9/{len(patients)}"
    return patients



# get one patient with report
@router.get("/{patient_id}")
def read_patient_by_id(
    patient_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific patient by id.
    """
    patient = crud.patient.get(db, id=patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="The Patient  with this Id does not exist in the system",
        )
    if patient.is_deleted:
        raise HTTPException(
            status_code=404,
            detail="The Patient is already deleted!",
        )

    #also check if the docktor that created the patient is the one updating
    if patient.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Un Authorised Access to entry you did'nt Author",
        )
    final_res =[]
    if patient:
        for patient_report in patient.report:
            if not patient_report.is_deleted:
                disease = s3.get_object(Bucket='sagemaker-us-east-1-472646256118',Key=f'{patient_report.annotation_path}')['Body'].read().decode('utf-8')
                final_res.append({'disease':disease, "details":patient_report})
    else:
        pass
    return {"patient":final_res}


@router.get("/doctor/all")
def read_docters_report(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get patients created by current dioctor.
    """
    patients = crud.patient.get_by_user_id(db, user_id=current_user.id)
    #"report":[r.report for r in patients]
    return {"patients":patients}


# TODO : DELETE PATIENT/REPORT
@router.delete("/{patient_id}")
def delete_patient_by_id(
    *,
    db: Session = Depends(deps.get_db),
    patient_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a patient.
    """
    patient = crud.patient.get(db, id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="The Patient  with this Id does not exist in the system or maybe deleted!",
        )

    if patient.is_deleted:
        raise HTTPException(
            status_code=404,
            detail="The Patient is already deleted!",
        )
    #also check if the docktor that created the patient is the one updating
    if patient.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Un Authorised Access to entry you did'nt Author",
        )
    #check if it exists;
    #save the data inot patient deleted objects
    try:
        patient_update = crud.patient.update(db, db_obj=patient, obj_in={"is_deleted":True})
        if crud.patient_delete.get_by_patient(db, id=patient.id):
            patient_deleted = crud.patient_delete.get_by_patient(db, id=patient.id)
        else:
            patient_deleted = crud.patient_delete.create(db, obj_in={"id":get_random_string(5, "deleted_object"), "patient_id":patient.id, "deleted_at":datetime.now()})
    except Exception as e:
        return {"message":f"An Error during Insertion i.e {e}!", "status":400}
    return {"patient deleted":patient_deleted, "delete status":"OK", "message":"Patient Deleted well"}


# TODO : DELETE PATIENT/REPORT
@router.delete("/report/{report_id}")
def delete_report_by_id(
    *,
    db: Session = Depends(deps.get_db),
    report_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a report.
    """
    report_instance = crud.report.get(db, id=report_id)
    if not report_instance:
        raise HTTPException(
            status_code=404,
            detail="The Report with such id does not exist in the system OR MAybe it was deleted",
        )
    if report_instance.is_deleted:
        raise HTTPException(
            status_code=404,
            detail="The Report is already deleted",
        )
    if report_instance.patient.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Un Authorised Access to entry you did'nt Author",
        )

    try:
        #save the data inot report deleted objects
        report_update = crud.report.update(db, db_obj=report_instance, obj_in={"is_deleted":True})
        if crud.report_delete.get_by_report(db,id=report_instance.id):
            report_deleted = crud.report_delete.get_by_report(db,id=report_instance.id)
        else:
            report_deleted = crud.report_delete.create(db,obj_in={"id":get_random_string(5, "deleted_report_"), "report_id":report_instance.id, "deleted_at":datetime.now()})
    except Exception as e:
        return {"message":f"An Error during Insertion i.e {e}!", "status":400}
    return {"Report deleted":report_deleted, "delete status":"OK", "message":"Report Deleted well"}



@router.get("/report/{report_id}")
def get_report(
    *,
    db: Session = Depends(deps.get_db),
    report_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    report_instance = crud.report.get(db, id=report_id)

    if not report_instance:
        raise HTTPException(
            status_code=404,
            detail="The Report with such id does not exist in the system",
        )

    if report_instance.is_deleted:
        raise HTTPException(
            status_code=404,
            detail="The Report was deleted from the server",
        )
    if report_instance.patient.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Un Authorised Access to entry you did'nt Author",
        )

    details = s3.get_object(Bucket='sagemaker-us-east-1-472646256118',Key=f'{report_instance.annotation_path}')['Body'].read().decode('utf-8')
    return {"details":report_instance, "disease":details}



@router.put("/report/update/{report_id}")
def update_report(
    *,
    db: Session = Depends(deps.get_db),
    report: str = Form(),
    report_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    report_instance = crud.report.get(db, id=report_id)

    if not report_instance:
        raise HTTPException(
            status_code=404,
            detail="The Report with such id does not exist in the system",
        )
    if report_instance.is_deleted:
        raise HTTPException(
            status_code=404,
            detail="Report Already Deleted",
        )
    #also check if the docktor that created the patient is the one updating
    if report_instance.patient.user_id != current_user.id:
        raise HTTPException(
        status_code=404,
        detail="Un Authorised Access to entry you did'nt Author",
        )
    report_update = crud.report.update(db, db_obj=report_instance, obj_in={"report":report})
    return report_update



@router.get('/file/annotation/{key}')
def read_annotation_from_aws(
*,
key: str ,
db: Session = Depends(deps.get_db),
current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    key ="Images/annotations/tb0003_20221221150357_zknhzijnoxzodho.txt"
    file = s3.get_object(Bucket='sagemaker-us-east-1-472646256118', Key=f'Images/annotations/{key}')
    content_type = file['ContentType']
    file_data = file['Body'].read().decode('utf-8')
    print(file_data)

    return {"data":file_data}

@router.get('/file/{img_type}/{image_id}')
def get_images_by_identifier(
*,
img_type: str,
image_id: str,
db: Session = Depends(deps.get_db),
# current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:

    if img_type not in ["profile", "inference", 'annotations', "imgs"]:
        raise HTTPException(
                        status_code=404,
                        detail="You must pass correct reference for image type, It must be part of this  (profile, inference, annotations, images)",
                    )

    try:
        file = s3.get_object(Bucket='sagemaker-us-east-1-472646256118', Key=f'Images/{img_type}/{image_id}')
    except Exception as e:
        print("Error Occured   ", e)
        error_msg = f"File does not exist - s3://sagemaker-us-east-1-472646256118/Images/{img_type}/{image_id}"
        raise HTTPException(
                        status_code=404,
                        detail=error_msg,
                    )

    content_type = file['ContentType']
    file = file['Body']

    img_extension = image_id.split(".")[-1]
    file_byte_string = file#self.s3.get_object(Bucket=bucket, Key=key)['Body'].read()
    # print(file_byte_string.read())
    file_byte_string = Image.open(BytesIO(file_byte_string.read()))
    filtered_image = BytesIO()
    file_byte_string.save(filtered_image, f"png")
    filtered_image.seek(0)

    return StreamingResponse(filtered_image, media_type=f"image/png")
