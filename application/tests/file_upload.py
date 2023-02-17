import json
from fastapi.testclient import TestClient
from fastapi.uploadfile import UploadFile
from io import BytesIO
from main import app

from helpers import get_random_string
from helperApp import *

def test_upload_file():
    client = TestClient(app)
    # create test file
    file = BytesIO(b"test file content")
    file.name = "test_file.txt"
    file.seek(0)
    #create fake patient
    fake_patient_id = "123456"
    crud.patient.create(db, id=fake_patient_id, user_id = current_user.id)

    #Test for successful upload
    response = client.post("/predict", data={"patient_id":fake_patient_id, "file": (file, "test_file.txt")}
    assert response.status_code == 200
    assert json.loads(response.text) == {"message": "File Uploaded Successfully!"}

    #Test for Missing file parameter
    response = client.post("/predict", data={"patient_id":fake_patient_id})
    assert response.status_code == 400
    assert json.loads(response.text) == {"message":"Missing file parameter!", "status":400}

    # Test non-existent patient
    response = client.post("/predict", data={"patient_id":"nonexistent_patient", "file": (file, "test_file.txt")})
    assert response.status_code == 404
    assert json.loads(response.text) == {"detail": "The Patient  with this Id does not exist in the system"}

    # Test Unauthorize Access
    fake_patient_id2 = "1234"
    crud.patient.create(db, id=fake_patient_id2, user_id = "fake_user")
    response = client.post("/predict", data={"patient_id":fake_patient_id2, "file": (file, "test_file.txt")})
    assert response.status_code == 404
    assert json.loads(response.text) == {"detail": "Un Authorised Access to entry you did'nt Author"}
