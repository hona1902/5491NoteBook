"""
Authentication router for Open Notebook API.
Provides endpoints for JWT auth and legacy status check.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from api.auth import create_access_token, get_current_user
from api.models import ChangePasswordRequest, LoginRequest, LoginResponse
from open_notebook.domain.user import AppUser, AppUserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status")
async def get_auth_status():
    """
    Check if authentication is enabled.
    JWT-based auth is always required.
    """
    return {
        "auth_enabled": True,
        "message": "Authentication is required",
    }


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = await AppUser.get_by_username(request.username_or_email)
    if not user:
        user = await AppUser.get_by_email(request.username_or_email)

    if not user or not user.verify_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    user.last_login_at = datetime.now(timezone.utc)
    await user.save()

    token = create_access_token({"sub": user.id})
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=AppUserResponse.from_user(user).model_dump(),
    )


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(current_user: AppUser = Depends(get_current_user)):
    return AppUserResponse.from_user(current_user).model_dump()


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: AppUser = Depends(get_current_user),
):
    if not current_user.verify_password(request.current_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.set_password(request.new_password)
    await current_user.save()
    return {"message": "Password changed successfully"}