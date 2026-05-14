"""
Admin router for user management.
All endpoints require admin role.
"""

from fastapi import APIRouter, Depends, HTTPException

from api.auth import require_admin
from api.models import AdminCreateUserRequest, AdminUpdateUserRequest
from open_notebook.database.repository import repo_query
from open_notebook.domain.user import AppUser, AppUserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(admin: AppUser = Depends(require_admin)):
    users = await AppUser.get_all()
    return [AppUserResponse.from_user(u).model_dump() for u in users]


@router.post("/users", status_code=201)
async def create_user(
    request: AdminCreateUserRequest,
    admin: AppUser = Depends(require_admin),
):
    existing = await AppUser.get_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing = await AppUser.get_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = await AppUser.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        role=request.role,
    )
    return AppUserResponse.from_user(user).model_dump()


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    request: AdminUpdateUserRequest,
    admin: AppUser = Depends(require_admin),
):
    try:
        user = await AppUser.get(user_id)
    except Exception:
        raise HTTPException(status_code=404, detail="User not found")

    if request.username is not None:
        existing = await AppUser.get_by_username(request.username)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Username already exists")
        user.username = request.username

    if request.email is not None:
        existing = await AppUser.get_by_email(request.email)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = request.email

    if request.role is not None:
        if user.role == "admin" and request.role != "admin":
            admin_count = await repo_query(
                "SELECT count() FROM app_user WHERE role = 'admin' GROUP ALL"
            )
            count = admin_count[0]["count"] if admin_count else 0
            if count <= 1:
                raise HTTPException(
                    status_code=400, detail="Cannot remove the last admin"
                )
        user.role = request.role

    if request.is_active is not None:
        user.is_active = request.is_active

    await user.save()
    return AppUserResponse.from_user(user).model_dump()


@router.patch("/users/{user_id}/password")
async def reset_user_password(
    user_id: str,
    new_password: str,
    admin: AppUser = Depends(require_admin),
):
    try:
        user = await AppUser.get(user_id)
    except Exception:
        raise HTTPException(status_code=404, detail="User not found")

    user.set_password(new_password)
    await user.save()
    return {"message": "Password reset successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: AppUser = Depends(require_admin),
):
    try:
        user = await AppUser.get(user_id)
    except Exception:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin":
        admin_count = await repo_query(
            "SELECT count() FROM app_user WHERE role = 'admin' GROUP ALL"
        )
        count = admin_count[0]["count"] if admin_count else 0
        if count <= 1:
            raise HTTPException(
                status_code=400, detail="Cannot delete the last admin"
            )

    await user.delete()
    return {"message": "User deleted successfully"}
