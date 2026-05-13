import paramiko
import time

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('160.30.113.168', username='root', password='Hoainam190291')

# 1. Update docker-compose.yml to use our custom-built image
print('Updating docker-compose.yml to use custom image...')
i, o, e = c.exec_command("sed -i 's|image: lfnovo/open_notebook:v1-latest|image: notebook-5491:latest|' /opt/5491NoteBook/docker-compose.yml")
print(o.read().decode())
print(e.read().decode())

# Also disable pull_policy for our custom image
i, o, e = c.exec_command("sed -i '/image: notebook-5491/,/pull_policy/{s/pull_policy: always/pull_policy: never/}' /opt/5491NoteBook/docker-compose.yml")
print(o.read().decode())
print(e.read().decode())

# Verify the change
print('\nUpdated docker-compose.yml:')
i, o, e = c.exec_command('cat /opt/5491NoteBook/docker-compose.yml')
print(o.read().decode())

# 2. Stop old container
print('\nStopping old notebook-5491 container...')
i, o, e = c.exec_command('docker stop notebook-5491 2>/dev/null; docker rm notebook-5491 2>/dev/null; echo DONE')
print(o.read().decode())

# Also stop any conflicting compose container
i, o, e = c.exec_command('cd /opt/5491NoteBook && docker compose down 2>&1')
print(o.read().decode())
print(e.read().decode())

time.sleep(3)

# 3. Start with docker compose
print('\nStarting with docker compose...')
i, o, e = c.exec_command('cd /opt/5491NoteBook && docker compose up -d 2>&1')
print(o.read().decode())
print(e.read().decode())

time.sleep(20)

# 4. Check status
print('\nContainer status:')
i, o, e = c.exec_command('docker ps --format "{{.Names}} {{.Status}}"')
print(o.read().decode())

# 5. Check logs
print('\nRecent logs:')
i, o, e = c.exec_command('cd /opt/5491NoteBook && docker compose logs open_notebook --tail 20 --no-log-prefix 2>&1 | grep -v TRACE | grep -v DEBUG')
print(o.read().decode())

c.close()
