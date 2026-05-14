# Design: VPS Redeployment

## Approach
Use SSH to connect to VPS, remove existing Docker setup, clone latest code from GitHub, and deploy using `Dockerfile.single` with a `docker-compose` override or direct `docker run`.

## Architecture
- **Single container**: `Dockerfile.single` includes SurrealDB + API + Frontend + Worker
- **Nginx**: Existing reverse proxy on VPS for domain `sotay5491.io.vn`
- **Volumes**: `/mydata` for SurrealDB, `/app/data` for app data

## Deployment Steps
1. SSH into VPS
2. Stop and remove all existing Docker containers and images
3. Clone the GitHub repo
4. Build Docker image from `Dockerfile.single`
5. Run container with proper env vars and volume mounts
6. Verify Nginx config points to correct ports
7. Test the application via domain
