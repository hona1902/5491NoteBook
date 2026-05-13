# Tasks: VPS Redeployment

- [ ] SSH into VPS (160.30.113.168)
- [ ] Stop and remove existing Docker containers
- [ ] Remove existing Docker images
- [ ] Remove old application directory (if any)
- [ ] Clone repo from https://github.com/hona1902/5491NoteBook
- [ ] Create `.env` file with proper configuration
- [ ] Build Docker image using `Dockerfile.single`
- [ ] Run the container with volume mounts and environment variables
- [ ] Verify Nginx reverse proxy config for sotay5491.io.vn
- [ ] Test application accessibility via domain
