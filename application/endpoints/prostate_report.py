import os
import torch
from fastapi import FastAPI, UploadFile, File
from monai.config import print_config
from monai.networks.nets import UNet
from monai.losses import DiceLoss
from monai.transforms import (
    LoadImage,
    AddChannel,
    Resize,
    CropForeground,
    ToTensor,
)

app = FastAPI()

print_config()

DEVICE = "cpu"
MODEL_PATH = "Best_model_Epoch.pth"
TRANSFORMS = [
    LoadImage(image_only=True),
    AddChannel(),
    Resize((192, 192, 16)),
    CropForeground(),
    ToTensor(),
]

# Load the pre-trained model
model = UNet(
    spatial_dims=3,
    in_channels=1,
    out_channels=2,
    channels=(16, 32, 64, 128, 256),
    strides=(2, 2, 2, 2),
    num_res_units=2,
    norm="batch",
).to(DEVICE)

model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))

# Define the loss function and optimizer
loss_fn = DiceLoss(to_onehot_y=True, softmax=True)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)


@app.post("/prostate_segmentation")
async def prostate_segmentation(file: UploadFile = File(...)):
    file_bytes = await file.read()
    image_tensor, _ = TRANSFORMS(file_bytes)
    image_tensor = image_tensor.to(DEVICE)

    # Run inference on the image
    with torch.no_grad():
        model.eval()
        logits = model(image_tensor.unsqueeze(0))
        prediction = torch.argmax(logits, dim=1)

    # Save the segmentation mask to a folder with id 12345
    os.makedirs("12345", exist_ok=True)
    save_path = os.path.join("12345", file.filename)
    torch.save(prediction, save_path)

    return {"filename": file.filename, "save_path": save_path}




# TO DEAL WITH prostate
# create report endpoint
# @router.post('/predict')
# async def upload_file(file: UploadFile,
# patient_id: str= Form(),
# db: Session = Depends(deps.get_db),
# current_user: models.User = Depends(deps.get_current_active_user),
# ):
#     # check if patient exists in the database...
#     #upload the text file
#     # checking if image uploaded is valid
#     patient = crud.patient.get(db, id=patient_id)
#     if not patient:
#         raise HTTPException(
#             status_code=404,
#             detail="The Patient  with this Id does not exist in the system Or maybe removed",
#         )
#
#     if patient.is_deleted:
#         raise HTTPException(
#             status_code=404,
#             detail="The Patient  is already deleted",
#         )
#     #also check if the docktor that created the patient is the one updating
#     if patient.user_id != current_user.id:
#         print(patient.user_id, current_user.id)
#         raise HTTPException(
#             status_code=404,
#             detail="Un Authorised Access to entry you did'nt Author",
#         )
#     #end
#
#     if file.filename == '':
#         return {"message":"Missing file parameter!", "status":400}
#
#     file_to_save =get_random_string(5, patient.user_id)
#     request_object_content = await file.read()
