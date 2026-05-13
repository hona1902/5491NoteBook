import paramiko
import time

HOST = "160.30.113.168"
USERNAME = "root"
PASSWORD = "Hoainam190291"

def ssh_command(command: str):
    print(f"\n--- Executing: {command} ---")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=HOST, username=USERNAME, password=PASSWORD, timeout=10)
        
        stdin, stdout, stderr = client.exec_command(command)
        
        # Wait for the command to finish
        exit_status = stdout.channel.recv_exit_status()
        
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        
        if out:
            print("STDOUT:")
            print(out)
        if err:
            print("STDERR:")
            print(err)
            
        print(f"Exit status: {exit_status}")
        client.close()
        return out
    except Exception as e:
        print(f"SSH Exception: {e}")
        return None

def main():
    print(f"Connecting to {HOST}...")
    
    # 1. Check running containers
    out = ssh_command("docker ps --format '{{.ID}}\t{{.Names}}\t{{.Image}}'")
    if not out:
        print("Could not get docker ps output.")
        return
        
    # Analyze the containers
    lines = out.strip().split('\n')
    container_name = None
    for line in lines:
        if 'backend' in line.lower() or 'api' in line.lower() or 'notebook' in line.lower():
            parts = line.split('\t')
            if len(parts) >= 2:
                container_name = parts[1]
                break
                
    if not container_name:
        print("No likely app container found from docker ps. Printing all:")
        print(out)
        # Just grab the first container if there's only one
        if len(lines) == 1 and bool(lines[0].strip()):
            container_name = lines[0].split('\t')[1]
            
    print("\n--- Watchdog Log ---")
    ssh_command("cat /root/watchdog.log | tail -n 20")
    print("\n--- Docker PS ---")
    ssh_command("docker ps")
    print("\n--- Docker Stats ---")
    ssh_command("docker stats --no-stream")


if __name__ == '__main__':
    main()
