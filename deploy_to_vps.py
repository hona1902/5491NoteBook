import paramiko
import sys
import time

def run_cmd(c, cmd):
    print(f"\n======================================")
    print(f"Running: {cmd}")
    stdin, stdout, stderr = c.exec_command(cmd, get_pty=True)
    
    # Stream output
    for line in iter(stdout.readline, ""):
        try:
            print(line, end="")
        except UnicodeEncodeError:
            print(line.encode('ascii', 'ignore').decode('ascii'), end="")
        
    status = stdout.channel.recv_exit_status()
    print(f"Command finished with exit code {status}")
    return status

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    print("Connecting to VPS...")
    c.connect('160.30.113.168', username='root', password='Hoainam190291', timeout=10)
    print("Connected!")
    
    # 1. Update source code
    run_cmd(c, "cd /opt/5491NoteBook && git fetch origin && git reset --hard origin/main")
    
    # 2. Re-apply docker-compose.yml modifications for VPS
    modify_compose = """
cd /opt/5491NoteBook
cat << 'EOF' > update_compose.py
import re
with open('docker-compose.yml', 'r') as f:
    content = f.read()

content = re.sub(r'image: lfnovo/open_notebook:.*', 'image: notebook-5491:latest', content)

# Change pull_policy for open_notebook specifically
content = re.sub(r'(open_notebook:.*?restart: always.*?)\s*pull_policy: always', r'\\1\\n    pull_policy: never', content, flags=re.DOTALL)

with open('docker-compose.yml', 'w') as f:
    f.write(content)
EOF
python3 update_compose.py
"""
    run_cmd(c, modify_compose)
    
    # Check what the compose file looks like now
    run_cmd(c, "cat /opt/5491NoteBook/docker-compose.yml")
    
    # 3. Build docker image
    run_cmd(c, "cd /opt/5491NoteBook && docker build -t notebook-5491:latest .")
    
    # 4. Restart services
    run_cmd(c, "cd /opt/5491NoteBook && docker compose down && docker compose up -d")
    
    print("\nDeployment completed successfully.")

except Exception as e:
    print(f"Error: {e}")
finally:
    c.close()
