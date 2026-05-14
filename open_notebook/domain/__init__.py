"""
Domain models for Open Notebook.

This module exports the core domain models used throughout the application.
"""

from open_notebook.domain.user import AppUser, AppUserResponse

__all__: list[str] = ["AppUser", "AppUserResponse"]
