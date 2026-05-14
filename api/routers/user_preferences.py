from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from api.auth import get_current_user
from api.models import UserPreferencesResponse, UserPreferencesUpdate
from open_notebook.domain.user import AppUser
from open_notebook.domain.user_preferences import UserPreferences

router = APIRouter()


@router.get("/users/me/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: AppUser = Depends(get_current_user),
):
    """Get the current user's preferences."""
    try:
        prefs = await UserPreferences.get_or_default(current_user.id)
        return UserPreferencesResponse(theme=prefs.theme)
    except Exception as e:
        logger.error(f"Error fetching preferences for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching preferences")


@router.patch("/users/me/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    update: UserPreferencesUpdate,
    current_user: AppUser = Depends(get_current_user),
):
    """Update the current user's preferences (upsert)."""
    try:
        prefs = await UserPreferences.get_for_user(current_user.id)
        if prefs:
            prefs.theme = update.theme
            await prefs.save()
        else:
            prefs = UserPreferences(user_id=current_user.id, theme=update.theme)
            await prefs.save()
        return UserPreferencesResponse(theme=prefs.theme)
    except Exception as e:
        logger.error(f"Error updating preferences for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating preferences")
