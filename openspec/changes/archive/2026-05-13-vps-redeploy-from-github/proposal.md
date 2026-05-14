# VPS Redeployment from GitHub

## Summary
Remove the existing Docker-based notebook application running on port 5400 on VPS `160.30.113.168`, and redeploy the latest version from GitHub repository `https://github.com/hona1902/5491NoteBook` using `Dockerfile.single` (all-in-one container with embedded SurrealDB). Continue using domain `sotay5491.io.vn`.

## Motivation
The current application on the VPS needs to be replaced with the latest source code that has been pushed to GitHub. This ensures the VPS runs the most up-to-date version of the application.

## Scope
- **VPS**: `160.30.113.168` (SSH root access)
- **Actions**: Stop & remove existing Docker containers/images → Clone repo → Build & run new container
- **Domain**: `sotay5491.io.vn` (Nginx reverse proxy already configured)
- **Ports**: Frontend on 8502, API on 5055 (internal); Nginx proxies from 80/443

## Risks
- Brief downtime during redeployment (~5-10 minutes)
- Existing data in SurrealDB may be lost if volumes are removed (need to assess whether to preserve)
