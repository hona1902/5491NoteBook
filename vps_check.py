import paramiko
import time

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('160.30.113.168', username='root', password='Hoainam190291')

# Upload the fixed file  
print("Uploading fixed chat.py...")
sftp = c.open_sftp()
sftp.put(
    r'd:\Project Web\TEST OPEN NOTEBOOK\api\routers\chat.py',
    '/opt/5491NoteBook/api/routers/chat.py'
)
sftp.close()

# Rebuild & deploy
print("Rebuilding Docker image...")
_, o, e = c.exec_command(
    'cd /opt/5491NoteBook && docker build -t notebook-5491:latest . 2>&1 | tail -5',
    timeout=600
)
build_out = o.read().decode()
print(build_out)

print("Restarting container...")
_, o, _ = c.exec_command(
    'cd /opt/5491NoteBook && docker compose up -d --force-recreate open_notebook 2>&1',
    timeout=60
)
print(o.read().decode())

print("Waiting 20s for startup...")
time.sleep(20)

# Verify sessions endpoint
print("Verifying sessions endpoint...")
_, o, _ = c.exec_command(
    'curl -s -k -H "Authorization: Bearer hoainam190291" '
    '"https://127.0.0.1/api/chat/sessions?notebook_id=notebook%3Aorsrbbj4tvvngnpg0o1d" '
    '-H "Host: sotay5491.io.vn" | head -c 500'
)
print(f"Sessions: {o.read().decode()}")

c.close()
print("\nDone!")
