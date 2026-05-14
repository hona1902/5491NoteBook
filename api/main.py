# Load environment variables
from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from open_notebook.exceptions import (
    AuthenticationError,
    ConfigurationError,
    ExternalServiceError,
    InvalidInputError,
    NetworkError,
    NotFoundError,
    OpenNotebookError,
    RateLimitError,
)
from api.routers import (
    admin,
    auth,
    chat,
    config,
    context,
    credentials,
    embedding,
    embedding_rebuild,
    episode_profiles,
    insights,
    languages,
    models,
    notebooks,
    notes,
    podcasts,
    search,
    settings,
    source_chat,
    sources,
    speaker_profiles,
    transformations,
    user_preferences,
)
from api.routers import commands as commands_router
from open_notebook.database.async_migrate import AsyncMigrationManager
from open_notebook.utils.encryption import get_secret_from_env

# Import commands to register them in the API process
try:
    logger.info("Commands imported in API process")
except Exception as e:
    logger.error(f"Failed to import commands in API process: {e}")


async def _bootstrap_admin_data(admin_user_id: str):
    """Assign all existing ownerless data to the bootstrap admin."""
    from open_notebook.database.repository import ensure_record_id, repo_query as _rq

    # Convert to RecordID — DB schema defines owner_id as option<record<app_user>>
    admin_record_id = ensure_record_id(admin_user_id)

    notes_result = await _rq(
        "UPDATE note SET owner_id = $admin_id WHERE owner_id = NONE",
        {"admin_id": admin_record_id},
    )
    notes_count = len(notes_result) if notes_result else 0

    sessions_result = await _rq(
        "UPDATE chat_session SET owner_id = $admin_id WHERE owner_id = NONE",
        {"admin_id": admin_record_id},
    )
    sessions_count = len(sessions_result) if sessions_result else 0

    notebooks_result = await _rq(
        "UPDATE notebook SET created_by = $admin_id WHERE created_by = NONE",
        {"admin_id": admin_record_id},
    )
    notebooks_count = len(notebooks_result) if notebooks_result else 0

    logger.info(
        f"Bootstrap data migration: {notes_count} notes, "
        f"{sessions_count} chat sessions, {notebooks_count} notebooks "
        f"assigned to admin {admin_user_id}"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    Runs database migrations automatically on startup.
    """
    import os

    # Startup: Security checks
    logger.info("Starting API initialization...")

    # Security check: Encryption key
    if not get_secret_from_env("OPEN_NOTEBOOK_ENCRYPTION_KEY"):
        logger.warning(
            "OPEN_NOTEBOOK_ENCRYPTION_KEY not set. "
            "API key encryption will fail until this is configured. "
            "Set OPEN_NOTEBOOK_ENCRYPTION_KEY to any secret string."
        )

    # Run database migrations

    try:
        migration_manager = AsyncMigrationManager()
        current_version = await migration_manager.get_current_version()
        logger.info(f"Current database version: {current_version}")

        if await migration_manager.needs_migration():
            logger.warning("Database migrations are pending. Running migrations...")
            await migration_manager.run_migration_up()
            new_version = await migration_manager.get_current_version()
            logger.success(
                f"Migrations completed successfully. Database is now at version {new_version}"
            )
        else:
            logger.info(
                "Database is already at the latest version. No migrations needed."
            )
    except Exception as e:
        logger.error(f"CRITICAL: Database migration failed: {str(e)}")
        logger.exception(e)
        # Fail fast - don't start the API with an outdated database schema
        raise RuntimeError(f"Failed to run database migrations: {str(e)}") from e

    # Run podcast profile data migration (legacy strings -> Model registry)
    try:
        from open_notebook.podcasts.migration import migrate_podcast_profiles

        await migrate_podcast_profiles()
    except Exception as e:
        logger.warning(f"Podcast profile migration encountered errors: {e}")
        # Non-fatal: profiles can be migrated manually via UI

    # JWT secret key check
    jwt_secret = os.environ.get("JWT_SECRET_KEY", "")
    if not jwt_secret:
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable is not set. "
            "Authentication cannot function without it."
        )

    # Admin bootstrap: create first admin user if app_user table is empty
    try:
        from open_notebook.database.repository import repo_query as _repo_query
        from open_notebook.domain.user import AppUser

        existing_users = await _repo_query("SELECT count() FROM app_user GROUP ALL")
        user_count = existing_users[0]["count"] if existing_users else 0

        if user_count == 0:
            admin_username = os.environ.get("ADMIN_USERNAME")
            admin_email = os.environ.get("ADMIN_EMAIL")
            admin_password = os.environ.get("ADMIN_PASSWORD")

            if admin_username and admin_email and admin_password:
                admin_user = await AppUser.create_user(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    role="admin",
                )
                logger.success(
                    f"Bootstrap: created admin user '{admin_username}' ({admin_user.id})"
                )

                # Migrate existing data to admin
                await _bootstrap_admin_data(admin_user.id)
            else:
                logger.warning(
                    "No users exist and ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD "
                    "not all set. Cannot bootstrap admin user."
                )
    except Exception as e:
        logger.error(f"Admin bootstrap error: {e}")
        # Non-fatal: admin can be created later

    logger.success("API initialization completed successfully")

    # Yield control to the application
    yield

    # Shutdown: cleanup if needed
    logger.info("API shutdown complete")


app = FastAPI(
    title="Open Notebook API",
    description="API for Open Notebook - Research Assistant",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler to ensure CORS headers are included in error responses
# This helps when errors occur before the CORS middleware can process them
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Custom exception handler that ensures CORS headers are included in error responses.
    This is particularly important for 413 (Payload Too Large) errors during file uploads.

    Note: If a reverse proxy (nginx, traefik) returns 413 before the request reaches
    FastAPI, this handler won't be called. In that case, configure your reverse proxy
    to add CORS headers to error responses.
    """
    # Get the origin from the request
    origin = request.headers.get("origin", "*")

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            **(exc.headers or {}), "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


def _cors_headers(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin", "*")
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
        headers=_cors_headers(request),
    )


@app.exception_handler(InvalidInputError)
async def invalid_input_error_handler(request: Request, exc: InvalidInputError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
        headers=_cors_headers(request),
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
        headers=_cors_headers(request),
    )


@app.exception_handler(RateLimitError)
async def rate_limit_error_handler(request: Request, exc: RateLimitError):
    return JSONResponse(
        status_code=429,
        content={"detail": str(exc)},
        headers=_cors_headers(request),
    )


@app.exception_handler(ConfigurationError)
async def configuration_error_handler(request: Request, exc: ConfigurationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
        headers=_cors_headers(request),
    )


@app.exception_handler(NetworkError)
async def network_error_handler(request: Request, exc: NetworkError):
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc)},
        headers=_cors_headers(request),
    )


@app.exception_handler(ExternalServiceError)
async def external_service_error_handler(request: Request, exc: ExternalServiceError):
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc)},
        headers=_cors_headers(request),
    )


@app.exception_handler(OpenNotebookError)
async def open_notebook_error_handler(request: Request, exc: OpenNotebookError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=_cors_headers(request),
    )


# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(notebooks.router, prefix="/api", tags=["notebooks"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(models.router, prefix="/api", tags=["models"])
app.include_router(transformations.router, prefix="/api", tags=["transformations"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(embedding.router, prefix="/api", tags=["embedding"])
app.include_router(
    embedding_rebuild.router, prefix="/api/embeddings", tags=["embeddings"]
)
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(context.router, prefix="/api", tags=["context"])
app.include_router(sources.router, prefix="/api", tags=["sources"])
app.include_router(insights.router, prefix="/api", tags=["insights"])
app.include_router(commands_router.router, prefix="/api", tags=["commands"])
app.include_router(podcasts.router, prefix="/api", tags=["podcasts"])
app.include_router(episode_profiles.router, prefix="/api", tags=["episode-profiles"])
app.include_router(speaker_profiles.router, prefix="/api", tags=["speaker-profiles"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(source_chat.router, prefix="/api", tags=["source-chat"])
app.include_router(credentials.router, prefix="/api", tags=["credentials"])
app.include_router(languages.router, prefix="/api", tags=["languages"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(user_preferences.router, prefix="/api", tags=["user-preferences"])


@app.get("/")
async def root():
    return {"message": "Open Notebook API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
