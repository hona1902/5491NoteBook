import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('160.30.113.168', username='root', password='Hoainam190291')

# We inject the environment variables into the docker-compose.yml file.
cmd = """
cd /opt/5491NoteBook
sed -i '/- API_URL=/a \      - ADMIN_USERNAME=admin\\n      - ADMIN_EMAIL=admin@mail.com\\n      - ADMIN_PASSWORD=admin' docker-compose.yml
docker compose down
docker compose build --no-cache
docker compose up -d
"""

stdin, stdout, stderr = client.exec_command(cmd)
print("STDOUT:", stdout.read().decode('utf-8'))
print("STDERR:", stderr.read().decode('utf-8'))
client.close()
