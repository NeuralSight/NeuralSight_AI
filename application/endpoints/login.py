from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud, model as models, schemas
from endpoints import deps
from core import security
from core.config import settings
from core.security import get_password_hash
from helpers import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)

import json

router = APIRouter()



@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    print("Request Has reeached Login....\n")
    # print(form_data.username, form_data.password)
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if user.is_superuser:
        permissions = "admin"
    else:
        permissions = "user"
    return {
        "access_token": security.create_access_token(
            permissions, user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/user/login/test", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/user/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    print(f"Restting...   {verify_password_reset_token(password_reset_token)}")
    return {"msg": f"Password recovery email sent  \n Token = {password_reset_token}"}


@router.post("/user/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    print("New Mail:  ", email)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}
