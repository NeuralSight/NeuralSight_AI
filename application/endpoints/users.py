from datetime import timedelta
from typing import Any, List
from core import security

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from tempfile import NamedTemporaryFile
import os
from typing import Union

import boto3, botocore
import crud, model as models, schemas
from endpoints import deps
from core.config import settings
from helpers import send_new_account_email

# files
from fastapi import UploadFile, File, Form

# s3
from helperApp import *
from dotenv import load_dotenv
load_dotenv()



router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = f"0-9/{len(users)}"
    return users





@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    # full_name: str = Form(),
    # email: EmailStr = Form(),
    # password : str = Form(),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=200,
            detail="The user is not allowed to create accoutn.",
        )
    print("USer in is ",user_in)
    user = crud.user.get_by_email(db, email=user_in.email)
    print(f"Current User Creating is  {current_user.is_superuser}")

    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    #need to check if hospital is already created...
    user = crud.user.create(db, obj_in=user_in)
    print(f"Mails  {settings.EMAILS_ENABLED}  and {user_in.email}")
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    else:
        print("Unable to send Email..")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if user.is_superuser:
        permissions = "admin"
    else:
        permissions = "user"
    print(f"User Id is  {user.id}, {user.email}, {user.full_name}")
    access_token = security.create_access_token(
        permissions, user.id, expires_delta=access_token_expires
    )
    print(f"Token   {access_token}")
    user.token = access_token
    return user #json.dumps({"user":{"email":user.email, "full_name":user.full_name}, "token":access_token})


# @router.put("/me", response_model=schemas.User)
# def update_user_me(
#     *,
#     db: Session = Depends(deps.get_db),
#     password: str = Body(None),
#     full_name: str = Body(None),
#     email: EmailStr = Body(None),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Update own user.
#     """
#     current_user_data = jsonable_encoder(current_user)
#     user_in = schemas.UserUpdate(**current_user_data)
#     if password is not None:
#         user_in.password = password
#     if full_name is not None:
#         user_in.full_name = full_name
#     if email is not None:
#         user_in.email = email
#     user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
#     return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/{user_id}")
def delete_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a user byy selected ID.
    """
    # check if the user to be deleted exists;
    user = crud.user.get(db, id=user_id)
    if user:
        user_delete = crud.user.remove(db=db, id=user_id)
        return {"user": user, "status":"OK", "message":"User has been Deleted Successful"}
    else:
        raise HTTPException(
            status_code=400, detail=f"The user with such Id {user_id} doesn't Exists in the System"
        )


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user





@router.put("/profile/update")
def update_userProfile(
    *,
    db: Session = Depends(deps.get_db),
    phone: str = Form(default=None),
    address: str = Form(default=None),
    location: str = Form(default=None),
    # hospital: str = Form(default=None),
    userProfile: Union[UploadFile, None] = File(default=None),
    # userProfile: UploadFile = File(default=None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user profile details.
    """

    user = current_user
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    if userProfile:
        temp = NamedTemporaryFile(delete=False)
        try:
            try:
                contents = userProfile.file#.read()
                # with temp as f:
                #     f.write(contents);
            except Exception:
                return {"message": "There was an error uploading the file"}
            finally:
                # Here, upload the file to your S3 service using `temp.name`
                s3.upload_fileobj(
                userProfile.file,
                os.getenv("AWS_BUCKET_NAME"),
                '%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv('AWS_PROFILE_FOLDER'),f"{user.full_name}_{userProfile.filename}"))
                userProfile.file.close()
        except Exception as e:
            return {"message": f"There was an error processing the file  as {e}"}
        finally:
            #temp.close()  # the `with` statement above takes care of closing the file
            os.remove(temp.name)  # Delete temp file
        # print(contents)  # Handle file contents as desired
        file_uploaded_path = '%s/%s/%s' % (f"{os.getenv('AWS_BUCKET_FOLDER')}", os.getenv('AWS_PROFILE_FOLDER'),f"{user.full_name}_{userProfile.filename}")
    else:
        file_uploaded_path = user.userProfile
    update_data = {
    "phone": phone if phone else user.phone,
    "address": address if address else user.address,
    "location": location if location else user.location,
    "userProfile": file_uploaded_path if userProfile else user.userProfile,
    }
    user = crud.user.update(db, db_obj=user, obj_in=update_data)
    user =crud.user.get(db, id=user.id)
    user.hashed_password =None
    return {"user": user, "status":"OK"}
