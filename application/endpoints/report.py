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

import json
# FastAPI and ORM
from fastapi import FastAPI, File, Form, UploadFile, APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

# Project's specific modules
from core import security
from core.config import settings
from endpoints import deps
from helpers import get_random_string
from helperApp import *
import crud, model as models, schemas
from fastapi.responses import StreamingResponse
from pydicom.uid import ExplicitVRLittleEndian





# s3 config
load_dotenv()

# Model Loading
# import wandb
# run = wandb.init()
# artifact = run.use_artifact('stephenkamau/YOLOv5/run_eoi3j9y3_model:v0', type='model')
# artifact_dir = artifact.download()

artifact_dir = "./endpoints"
# print("artifact Dir: ",artifact_dir, os.path.isfile("./endpoints/best.pt"))
#
# # load model
torch.hub._validate_not_a_forked_repo=lambda a,b,c: True
model = torch.hub.load('ultralytics/yolov5', 'custom', path=f"{artifact_dir}/best.pt", force_reload=True)





router = APIRouter()


import tempfile
import pydicom
from io import BytesIO
import requests
from pydicom.encaps import encapsulate
ORTHANC_URL = f"{os.getenv('ORTHANC_URL')}"
# http://localhost:8042
#

print(f"OTHANK URL   {ORTHANC_URL}")
# from monai.config import print_config
# from monai.networks.nets import UNet
# from monai.losses import DiceLoss
# from monai.transforms import (
#     LoadImage,
#     AddChannel,
#     Resize,
#     CropForeground,
#     ToTensor,
# )
# from monai.transforms import LoadImaged, AddChanneld, ToTensord, Resized, Compose, EnsureChannelFirstd
#
#
# DEVICE = "cpu"
# MODEL_PATH = "./endpoints/Best_model_Epoch_.pth"
#
# # TRANSFORMS = [
# #     LoadImage(image_only=True),
# #     AddChannel(),
# #     Resize((192, 192, 16)),
# #     CropForeground(),
# #     ToTensor(),
# # ]
#
# TRANSFORMS = Compose(
#     [
#         LoadImage(image_only=True),
#         AddChannel(),
#         Resize((192, 192, 16)),
#         CropForeground(),
#         ToTensor(),
#     ]
# )
#
# # Load the pre-trained model
# model1 = UNet(
#     spatial_dims=3,
#     in_channels=1,
#     out_channels=2,
#     channels=(16, 32, 64, 128, 256),
#     strides=(2, 2, 2, 2),
#     num_res_units=2,
#     norm="batch",
# ).to(DEVICE)
#
# model1.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
#
# # Define the loss function and optimizer
# loss_fn = DiceLoss(to_onehot_y=True, softmax=True)
# optimizer = torch.optim.Adam(model1.parameters(), lr=1e-4)
#
#
# @router.post("/prostate_segmentation")
# async def prostate_segmentation(file: UploadFile = File(...)):
#     file_bytes = await file.read()
#     image_tensor, _ = TRANSFORMS(file_bytes)
#     image_tensor = image_tensor.to(DEVICE)
#
#     # Run inference on the image
#     with torch.no_grad():
#         model1.eval()
#         logits = model(image_tensor.unsqueeze(0))
#         prediction = torch.argmax(logits, dim=1)
#
#     # Save the segmentation mask to a folder with id 12345
#     os.makedirs("12345", exist_ok=True)
#     save_path = os.path.join("12345", file.filename)
#     torch.save(prediction, save_path)
#
#     return {"filename": file.filename, "save_path": save_path}



def modify_dicom_metadata(input_file_path, new_metadata, file_refence):
    # Read the DICOM file
    dicom_data = pydicom.dcmread(input_file_path)
    patient_id = str(pydicom.uid.generate_uid())

    # Modify the metadata
    for tag, value in new_metadata.items():
        if tag in dicom_data:
            dicom_data[tag].value = value
        else:
            pass
            # element = pydicom.DataElement(tag, dicom_data.file_meta[tag].VR, value)
            # dicom_data.add(element)

    # Generate unique identifiers for SOPInstanceUID, PatientID, and StudyID

    patient_name_str = str(file_refence)
    new_patient_name_str = patient_name_str + "_Image_Converted"
    new_patient_name = pydicom.valuerep.PersonName(new_patient_name_str)
    dicom_data.PatientName = new_patient_name
    dicom_data.PatientID = f"{patient_id}_predicted"
    dicom_data.SOPInstanceUID = pydicom.uid.generate_uid()
    dicom_data.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    dicom_data.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    dicom_data.StudyID = pydicom.uid.generate_uid()
    dicom_data.StudyInstanceUID = pydicom.uid.generate_uid()
    dicom_data.SeriesInstanceUID = pydicom.uid.generate_uid()
    # dicom_data.ParentPatient = pydicom.uid.generate_uid()
    # dicom_data.ParentStudy = pydicom.uid.generate_uid()
    # dicom_data.ParentSeries = pydicom.uid.generate_uid()
    # Generate UIDs if they are missing
    return dicom_data


def modify_dicom_metadata_pred(dicom_data, new_metadata, file_refence):
    # Read the DICOM file

    patient_id = str(pydicom.uid.generate_uid())

    # Modify the metadata
    for tag, value in new_metadata.items():
        if tag in dicom_data:
            dicom_data[tag].value = value
        else:
            pass
    # Generate unique identifiers for SOPInstanceUID, PatientID, and StudyID
    new_patient_name_str = file_refence + "_PREDICTED"
    new_patient_name = pydicom.valuerep.PersonName(new_patient_name_str)
    dicom_data.PatientName = new_patient_name
    dicom_data.PatientID = f"{patient_id}_predicted"
    dicom_data.SOPInstanceUID = pydicom.uid.generate_uid()
    dicom_data.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    dicom_data.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    dicom_data.StudyID = pydicom.uid.generate_uid()
    dicom_data.StudyInstanceUID = pydicom.uid.generate_uid()
    dicom_data.SeriesInstanceUID = pydicom.uid.generate_uid()
    return dicom_data


def predict_png_image(request_object_content, file_refence):
    patient_id = str(pydicom.uid.generate_uid())
    uploaded_img = Image.open(io.BytesIO(request_object_content))
    results = model(uploaded_img, size=640)

    annotations_image = []
    results.render()

    dicom_data = modify_dicom_metadata("ID_00528aa0e.dcm",{'PatientName': '','PatientAge': '','StudyDescription': 'Created',}, file_refence)


    # dicom_data.BitsAllocated = 16
    # dicom_data.BitsStored = 16
    # dicom_data.HighBit = 15

    dicom_data.Rows = results.ims[0].shape[0]
    dicom_data.Columns = results.ims[0].shape[1]
    dicom_data.PhotometricInterpretation = "MONOCHROME2"
    cv2.imwrite("let.png", results.ims[0])
    dicom_data.PixelData = np.array(Image.open("let.png").convert("L")).tobytes()
    # print(dicom_data.pixel_array)

    # dicom_data.PixelData =cv2.imencode('.png', results.ims[0])[1].tobytes() #results.ims[0].tobytes()
    # patient_name_str =  "Created_instance"
    # new_patient_name_str = patient_name_str + "_PREDICTED"
    # new_patient_name = pydicom.valuerep.PersonName(new_patient_name_str)
    # dicom_data.PatientName = new_patient_name
    # dicom_data.PatientID = f"{str(pydicom.uid.generate_uid())}_predicted"
    # file_meta = pydicom.Dataset()
    # sop_instance_uid = pydicom.uid.generate_uid()
    # Set the SOP Instance UID in the dataset
    # dicom_data.SOPInstanceUID = sop_instance_uid
    # file_meta.MediaStorageSOPInstanceUID = dicom_data.SOPInstanceUID
    # file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    # Set the file meta information in the dataset
    # dicom_data.file_meta = file_meta

    x = dict({a[1]:a[0]   for a in  [[results.names.get(int(a), None) if item.index(a)==5 else a for a in item[-2:]] for item in results.pred[0].tolist()]})

    predict_results = {"name": results.names, "preds":x}

    return dicom_data, predict_results


def predict_dicom_chest(model, input_bytes):
    """
    Uses the model to predicted results of a dicom image
    """
    dicom = pydicom.dcmread(BytesIO(input_bytes))
    img = dicom.pixel_array.astype(np.float32)
    # print(f"Array Shape is  {img.shape}")
    results = model(img, size=640)


    return results, dicom



# orthankSaver
@router.post("/models")
async def models_handler():
    answer = {
        "pathologies": "pathologies",
        "pneumonia": "pneumonia",
    }
    return answer




@router.post("/upload", response_model=schemas.OrthancBaseOptional)
def create_predicted_data(
    *,
    db: Session = Depends(deps.get_db),
    details: schemas.OrthancCreate,
) -> Any:
    try:
        saved_details = crud.orthankSaver.create(db, obj_in=dict(details))
        return  schemas.OrthancBaseOptional(
            ID=saved_details.ID,
            ParentPatient=saved_details.ParentPatient,
            ParentSeries=saved_details.ParentSeries,
            ParentStudy=saved_details.ParentStudy,
            Path=saved_details.Path,
            results=saved_details.results,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occurred during data upload. Duplicate Keys   {e}")




@router.get("/dicom/{dicom_uuid}", response_model=schemas.OrthancBaseOptional)
def read_dicom_by_uuid(
    uuid: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific dicom by id.
    """
    saved_details = crud.orthankSaver.get(db, id=uuid)
    if saved_details:
        return schemas.OrthancBaseOptional(
            ID=saved_details.ID,
            ParentPatient=saved_details.ParentPatient,
            ParentSeries=saved_details.ParentSeries,
            ParentStudy=saved_details.ParentStudy,
            Path=saved_details.Path,
            results=json.loads(saved_details.results),
        )
    raise HTTPException(
        status_code=400, detail="No Item with Such UUID"
    )


#
#
@router.get("/find/all", response_model=List[schemas.OrthancBaseOptional])
def read_all_ids_saved(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    data = crud.orthankSaver.get_multi_data(db, skip=skip, limit=limit)
    if data:
        results = [
        schemas.OrthancBaseOptional(
            ID=saved_details.ID,
            ParentPatient=saved_details.ParentPatient,
            ParentSeries=saved_details.ParentSeries,
            ParentStudy=saved_details.ParentStudy,
            Path=saved_details.Path,
            results=json.loads(saved_details.results),
        )  for saved_details in data
        ]
        response.headers["Access-Control-Expose-Headers"] = "Content-Range"
        response.headers["Content-Range"] = f"0-9/{len(results)}"
        return results
    else:
        return []




@router.post("/authorise")
async def request_handler():
    answer = {
        "granted": True  # Forbid access
    }
    return answer

@router.post("/dicom/instances")
def fetch_dicom_images(
username: str = Form(),
password: str = Form()
):
    url = f'{ORTHANC_URL}/instances'
    response = requests.get(url,auth=requests.auth.HTTPBasicAuth(f"{username}", f"{password}"))

    if response.status_code == 401:
        raise HTTPException(
            status_code=401,
            detail="Please Provide correct credentials. Not Authorised to access this service",
        )
    if response.status_code == 200:
        return {"instance_ids":response.json()}
    else:
        print(response.text)
        return {"error": "Failed to fetch DICOM images"}


@router.post("/dicom/pred")
async def prostate_segmentation(
file: UploadFile = File(...),
username: str = Form(),
password: str = Form(),
file_refence: str = Form(None),
db: Session = Depends(deps.get_db),
# current_user: models.User = Depends(deps.get_current_active_user)
):
    # Read the uploaded DICOM file
    url = f'{ORTHANC_URL}/instances'
    file_bytes = await file.read()
    response1 ={}
    patient_id = str(pydicom.uid.generate_uid())

    if not file_refence:
        file_refence = "patient_file"
    try:
        # Check if the file is in DICOM format
        file_type =file.content_type
        if file_type == "image/jpeg" or file_type == "image/png":
            is_dicom = False
            final_dicom, res =  predict_png_image(file_bytes, file_refence)
            buffer = BytesIO()
            pydicom.dcmwrite(buffer, final_dicom)
            buffer.seek(0)

            # get the contents of the BytesIO object as bytes
            file_bytes = buffer.read()
            #save back the results
            response2 = requests.post(url, data=file_bytes, auth=requests.auth.HTTPBasicAuth(f"{username}", f"{password}"))
            if response2.status_code == 401:
                return HTTPException(
                    status_code=401,
                    detail="Please Provide correct credentials. Not Authorised to access this service",
                )
            if response2.status_code != 200:
                print("An issue,  ",response2.text)
                return {"error": f"Error sending file to Orthancqq: {response2.content}"}


            #
            # x = dict({a[1]:a[0]   for a in  [[res.names.get(int(a), None) if item.index(a)==5 else a for a in item[-2:]] for item in res.pred[0].tolist()]})
            response2 = response2.json()

            try:
                data_to_save = {
                "ID":response2['ID'],
                "ParentPatient":response2['ParentPatient'],
                "ParentSeries":response2['ParentSeries'],
                "ParentStudy":response2['ParentStudy'],
                "Path":response2['Path'],
                "results":res,
                }
                saved_details = crud.orthankSaver.create(db, obj_in=data_to_save)

            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occurred during data upload.  {e}")

            return {"uploaded_details": {}, "predicted_details": response2, "results":data_to_save}

        elif file_type == "application/dicom":
            is_dicom = True
            dicom_img = pydicom.dcmread(BytesIO(file_bytes))
            dicom_img.PatientID = patient_id
            # change the name//
            new_patient_name = pydicom.valuerep.PersonName(file_refence + "_Uploaded")
            dicom_img.PatientName = new_patient_name
            # Generate UIDs if they are missing
            if not dicom_img.SeriesInstanceUID:
                dicom_img.SeriesInstanceUID = pydicom.uid.generate_uid()
            if not dicom_img.SOPInstanceUID:
                dicom_img.SOPInstanceUID = pydicom.uid.generate_uid()
            if not dicom_img.StudyInstanceUID:
                dicom_img.StudyInstanceUID = pydicom.uid.generate_uid()
            # write the DICOM file to a BytesIO object
            buffer = BytesIO()
            pydicom.dcmwrite(buffer, dicom_img)
            buffer.seek(0)
            file_bytes = buffer.read()

            response1 = requests.post(url, data=file_bytes, auth=requests.auth.HTTPBasicAuth(f"{username}", f"{password}"))
            print("Current Status code:   ",response1.status_code)
            # print(dicom_img.pixel_array)
            if response1.status_code == 401:
                return HTTPException(
                    status_code=401,
                    detail="Please Provide correct credentials. Not Authorised to access this service",
                )
            if response1.status_code != 200:
                return {"error": f"Error sending file to Orthanc: {response1.content}"}
            else:
                print(f"Results is   {response1.json()}")
        else:
            return {"error": f"Error: Only png, Jpeg and dicom file types are allowed..."}
        print("Uploaded File Type:", file_type)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error sending file to Orthanc: {e}")

    try:
        res, dicom_data = predict_dicom_chest(model, file_bytes)
        res.render()
        #
        # # Create a new DICOM file with the results
        print(f"Total Number of Images are  {len(res.ims)}")
        # dicom_data.BitsAllocated = 16
        # dicom_data.BitsStored = 16
        # dicom_data.HighBit = 15

        dicom_data = dicom_data = modify_dicom_metadata_pred(dicom_data, {'PatientName': '','PatientAge': '','StudyDescription': 'Created',}, file_refence)

        dicom_data.Rows = res.ims[0].shape[0]
        dicom_data.Columns = res.ims[0].shape[1]
        dicom_data.PhotometricInterpretation = "MONOCHROME2"
        cv2.imwrite("let1.png", res.ims[0])
        dicom_data.PixelData = np.array(Image.open("let1.png").convert("L")).tobytes()

        print(f"Predicted Shape is {res.ims[0].shape}")

        # write the DICOM file to a BytesIO object
        buffer = BytesIO()
        pydicom.dcmwrite(buffer, dicom_data)
        buffer.seek(0)

        # get the contents of the BytesIO object as bytes
        file_bytes = buffer.read()
        #save back the results
        files = {'file': ("preds_"+file.filename, file_bytes, 'application/dicom')}
        response2 = requests.post(url, data=file_bytes, auth=requests.auth.HTTPBasicAuth(f"{username}", f"{password}"))
        print("Preds Status code:   ",response2.status_code)
        if response2.status_code == 401:
            return HTTPException(
                status_code=401,
                detail="Please Provide correct credentials. Not Authorised to access this service",
            )
        if response2.status_code != 200:
            print("An issue,  ",response2.text)
            return {"error": f"Error sending file to Orthancqq: {response2.content}"}
        else:
            if is_dicom:
                print(f"Preds is  {response1.json()}")

        x = dict({a[1]:a[0]   for a in  [[res.names.get(int(a), None) if item.index(a)==5 else a for a in item[-2:]] for item in res.pred[0].tolist()]})


        response2 = response2.json()
        data_to_save = {
        "ID":response2['ID'],
        "ParentPatient":response2['ParentPatient'],
        "ParentSeries":response2['ParentSeries'],
        "ParentStudy":response2['ParentStudy'],
        "Path":response2['Path'],
        "results":x,
        }
        saved_details = crud.orthankSaver.create(db, obj_in=data_to_save)
        # print(f"DATA SAVED    ", saved_details)


        return {"uploaded_details": response1.json() if is_dicom else [], "predicted_details": response2, "results":data_to_save}
    except Exception as e:
        # print(f"ERROROROR   {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error sending file to Orthanc: {e}")

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
