import paramiko
import sys

def run_cmd(c, cmd):
    print(f"Running: {cmd}")
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"STDOUT:\n{out}")
    if err:
        print(f"STDERR:\n{err}")
    return out

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    c.connect('160.30.113.168', username='root', password='Hoainam190291', timeout=10)
    print("Connected!")
    
    run_cmd(c, "ls -la /opt/5491NoteBook")
    run_cmd(c, "cd /opt/5491NoteBook && git status")
    run_cmd(c, "docker ps")
    
finally:
    c.close()
