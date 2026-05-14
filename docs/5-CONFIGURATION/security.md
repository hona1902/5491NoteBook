# Security Configuration

Protect your Open Notebook deployment with JWT-based multi-user authentication and production hardening.

---

## Authentication System

Open Notebook uses JWT (JSON Web Token) authentication with multi-user support. Each user has their own account with role-based access control.

### Key Features

| Feature | Description |
|---------|-------------|
| Multi-user | Individual accounts with username/email login |
| Role-based access | `admin` and `user` roles |
| JWT tokens | Stateless authentication with configurable expiry |
| Password hashing | Argon2id (memory-hard, resistant to GPU attacks) |
| Data isolation | Users only see their own notes and chat sessions |
| Admin bootstrap | First admin created automatically from environment variables |

### Roles

| Role | Permissions |
|------|-------------|
| `admin` | Create/edit/delete notebooks, manage users, full access |
| `user` | View notebooks, create notes/chats (own data only) |

---

## Quick Setup

### Required Environment Variables

```yaml
# docker-compose.yml
environment:
  # REQUIRED: Secret key for signing JWT tokens
  - JWT_SECRET_KEY=your-random-secret-string-here

  # REQUIRED: First admin account (created on empty database)
  - ADMIN_USERNAME=admin
  - ADMIN_EMAIL=admin@example.com
  - ADMIN_PASSWORD=your-secure-admin-password

  # Optional: Token expiry (default: 24 hours)
  # - JWT_ACCESS_TOKEN_EXPIRE_HOURS=24
```

### First-Time Setup

1. Set the environment variables above in your `docker-compose.yml` or `.env` file
2. Start the application — the admin account is created automatically on first boot
3. Log in at the web UI with your admin credentials
4. Create additional users via **Admin → Users** in the sidebar

### Generating a JWT Secret

```bash
# Linux/macOS
openssl rand -base64 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use a unique, random string of at least 32 characters. Never reuse secrets across deployments.

---

## API Key Encryption

Open Notebook encrypts AI provider API keys stored in the database using Fernet symmetric encryption (AES-128-CBC with HMAC-SHA256).

### Setup

Set the encryption key to any secret string:

```bash
# .env or docker-compose.yml
OPEN_NOTEBOOK_ENCRYPTION_KEY=my-secret-passphrase
```

Any string works — it will be securely derived via SHA-256 internally. Use a strong passphrase for production deployments.

**The encryption key has no default.** You must set `OPEN_NOTEBOOK_ENCRYPTION_KEY` before using the API key configuration feature.

### Docker Secrets Support

```yaml
environment:
  - OPEN_NOTEBOOK_ENCRYPTION_KEY_FILE=/run/secrets/encryption_key
```

### Key Management

- **Keep secret**: Never commit the encryption key to version control
- **Backup securely**: Store the key separately from database backups
- **No rotation yet**: Changing the key requires re-saving all API keys
- **Per-deployment**: Each instance should have its own encryption key

---

## API Authentication

### Login

```bash
# Get a JWT token
curl -X POST http://localhost:5055/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "admin", "password": "your-password"}'

# Response:
# {"access_token": "eyJ...", "token_type": "bearer", "user": {...}}
```

### Authenticated Requests

```bash
# Use the token in subsequent requests
TOKEN="eyJ..."

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5055/api/notebooks

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Notebook", "description": "Research notes"}' \
  http://localhost:5055/api/notebooks
```

### Unprotected Endpoints

These work without authentication:

- `/health` - System health check
- `/docs` - API documentation
- `/openapi.json` - OpenAPI spec
- `/api/auth/login` - Login endpoint

---

## User Management

### Admin Panel

Admins can manage users through the web UI at **Admin → Users**:

- Create new users (username, email, password, role)
- Toggle user active/inactive status
- Reset user passwords
- Delete users (cannot delete the last admin)

### Admin API Endpoints

```bash
TOKEN="eyJ..."  # Must be an admin token

# List all users
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5055/api/admin/users

# Create user
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "researcher", "email": "r@example.com", "password": "secure123", "role": "user"}' \
  http://localhost:5055/api/admin/users

# Deactivate user
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}' \
  http://localhost:5055/api/admin/users/app_user:abc123

# Reset password
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_password": "new-secure-password"}' \
  http://localhost:5055/api/admin/users/app_user:abc123/password

# Delete user
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  http://localhost:5055/api/admin/users/app_user:abc123
```

---

## Data Isolation

Each user's data is isolated by default:

| Resource | Behavior |
|----------|----------|
| Notes | Users only see/edit their own notes |
| Chat sessions | Users only see/edit their own chats |
| Notebooks | All users can view; only admins can create/edit/delete |
| Sources | Shared within notebooks (visible to all users with notebook access) |

Attempting to access another user's notes or chat sessions returns HTTP 404 (not 403), preventing information leakage about resource existence.

---

## Production Hardening

### Docker Security

```yaml
services:
  open_notebook:
    image: lfnovo/open_notebook:v1-latest
    pull_policy: always
    ports:
      - "127.0.0.1:8502:8502"  # Bind to localhost only
      - "127.0.0.1:5055:5055"
    environment:
      - OPEN_NOTEBOOK_ENCRYPTION_KEY=your-strong-secret-key
      - JWT_SECRET_KEY=your-random-jwt-secret
      - ADMIN_USERNAME=admin
      - ADMIN_EMAIL=admin@yourdomain.com
      - ADMIN_PASSWORD=your-secure-admin-password
    security_opt:
      - no-new-privileges:true
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
    restart: always
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8502/tcp   # Block direct access
sudo ufw deny 5055/tcp   # Block direct API access
sudo ufw enable
```

### Reverse Proxy with SSL

See [Reverse Proxy Configuration](reverse-proxy.md) for complete nginx/Caddy/Traefik setup with HTTPS.

### Security Checklist

- [ ] Set a strong, unique `JWT_SECRET_KEY` (32+ characters)
- [ ] Set a strong `ADMIN_PASSWORD` (not the default)
- [ ] Set `OPEN_NOTEBOOK_ENCRYPTION_KEY` for credential storage
- [ ] Use HTTPS via reverse proxy (JWT tokens are sent in headers)
- [ ] Bind ports to localhost only (use reverse proxy for external access)
- [ ] Change default SurrealDB credentials (`SURREAL_USER`, `SURREAL_PASSWORD`)
- [ ] Keep containers and dependencies updated
- [ ] Monitor logs for suspicious activity

---

## Security Properties

| Feature | Status |
|---------|--------|
| Token format | JWT (HS256) |
| Token expiry | 24 hours (configurable) |
| Password hashing | Argon2id |
| Data isolation | Per-user (owner_id enforcement) |
| Role-based access | Admin / User roles |
| Login error messages | Generic (no user enumeration) |
| Rate limiting | None (add at proxy layer) |
| Audit logging | None |

### Risk Mitigation

1. **Always use HTTPS** — JWT tokens in headers must be encrypted in transit
2. **Strong JWT secret** — 32+ random characters, unique per deployment
3. **Strong admin password** — Change from default immediately
4. **Network security** — Firewall, VPN for sensitive deployments
5. **Regular updates** — Keep containers and dependencies updated
6. **Backups** — Regular backups of data and encryption keys

---

## Troubleshooting

### Cannot Log In

1. Check that `ADMIN_USERNAME` and `ADMIN_PASSWORD` are set in environment
2. Check API logs: `docker logs <container> | grep -i auth`
3. Verify the admin was bootstrapped: look for "Created initial admin user" in startup logs
4. Try logging in with email instead of username

### 401 Unauthorized Errors

```bash
# Test login
curl -X POST http://localhost:5055/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "admin", "password": "your-password"}'

# Check token works
curl -H "Authorization: Bearer <token-from-login>" \
  http://localhost:5055/api/auth/me
```

### "Account is disabled" Error

An admin has deactivated the user account. Contact your administrator to re-enable it.

### JWT_SECRET_KEY Not Set

The application will fail to start with a `RuntimeError` if `JWT_SECRET_KEY` is not set. Add it to your environment configuration.

### Admin Bootstrap Not Running

The admin is only created when the `app_user` table is empty. If you already have users, the bootstrap is skipped. Create additional admins via the admin panel or API.

---

## Reporting Security Issues

If you discover security vulnerabilities:

1. **Do NOT open public issues**
2. Contact maintainers directly
3. Provide detailed information
4. Allow time for fixes before disclosure

---

## Related

- **[Reverse Proxy](reverse-proxy.md)** - HTTPS and SSL setup
- **[Advanced Configuration](advanced.md)** - Ports, timeouts, and SSL settings
- **[Environment Reference](environment-reference.md)** - All configuration options
