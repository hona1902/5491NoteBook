import paramiko
import json
import time

VPS_HOST = "160.30.113.168"
VPS_USER = "root"
VPS_PASS = "Hoainam190291"
API_BASE = "https://sotay5491.io.vn/api"
AUTH = "hoainam190291"
NB_ID = "notebook:orsrbbj4tvvngnpg0o1d"
NUM_REQUESTS = 10

QUESTIONS = [
    "Kế toán là gì? Trả lời ngắn gọn 1-2 câu.",
    "Nguyên tắc kế toán cơ bản? Trả lời ngắn.",
    "Tài sản và nguồn vốn khác nhau thế nào? 1 câu.",
    "Báo cáo tài chính gồm những gì? Liệt kê ngắn.",
    "Thuế GTGT là gì? 1 câu.",
    "Doanh thu và lợi nhuận khác nhau? Trả lời ngắn.",
    "Khấu hao tài sản là gì? 1-2 câu.",
    "Kế toán kép là gì? 1 câu.",
    "Bảng cân đối kế toán gồm gì? Ngắn gọn.",
    "Chi phí cố định và chi phí biến đổi? 1 câu."
]

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS)

report = []

def log(msg):
    report.append(msg)

log(f"{'='*60}")
log(f"STRESS TEST — 10 sessions x {NB_ID}")
log(f"Via: {API_BASE}")
log(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
log(f"{'='*60}")

# Step 1: Create 10 sessions
log("\n=== CREATING 10 SESSIONS ===")
session_ids = []
for i in range(NUM_REQUESTS):
    cmd = (
        f'curl -s -k -X POST '
        f'-H "Authorization: Bearer {AUTH}" '
        f'-H "Content-Type: application/json" '
        f'-d \'{{"notebook_id":"{NB_ID}","title":"StressTest-{i}"}}\' '
        f'{API_BASE}/chat/sessions'
    )
    _, o, _ = c.exec_command(cmd)
    result = o.read().decode()
    try:
        data = json.loads(result)
        session_ids.append(data["id"])
        log(f"  ✓ Session {i}: {data['id']}")
    except:
        log(f"  ✗ Session {i} FAILED: {result[:150]}")
        session_ids.append(None)

valid_count = sum(1 for s in session_ids if s)
log(f"\n  Created: {valid_count}/{NUM_REQUESTS} sessions")

if valid_count == 0:
    log("ABORT: No sessions created")
    with open(r'd:\temp_stress_test.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    c.close()
    print("Report written. ABORT.")
    exit(1)

# Step 2: Mark log position
_, o, _ = c.exec_command('cd /opt/5491NoteBook && docker compose logs open_notebook --no-log-prefix 2>&1 | wc -l')
log_before = int(o.read().decode().strip())

# Step 3: Fire 10 concurrent chat requests
log(f"\n=== FIRING {NUM_REQUESTS} CONCURRENT CHAT REQUESTS ===")
sftp = c.open_sftp()
script_lines = ["#!/bin/bash", "rm -rf /tmp/stress_test", "mkdir -p /tmp/stress_test", ""]

for i, sid in enumerate(session_ids):
    if not sid:
        continue
    payload = json.dumps({
        "session_id": sid,
        "message": QUESTIONS[i],
        "context": {"sources": [], "notes": [], "insights": []},
    })
    script_lines.append(
        f'curl -s -k --max-time 120 -X POST '
        f'-H "Authorization: Bearer {AUTH}" '
        f'-H "Content-Type: application/json" '
        f"-d '{payload}' "
        f'{API_BASE}/chat/execute > /tmp/stress_test/r{i}.json 2>&1 &'
    )

script_lines.append("")
script_lines.append("wait")
script_lines.append('echo "ALL_DONE"')

with sftp.file('/tmp/run_stress.sh', 'w') as f:
    f.write("\n".join(script_lines))
sftp.close()

start = time.time()
_, o, _ = c.exec_command("bash /tmp/run_stress.sh", timeout=180)
output = o.read().decode()
elapsed = time.time() - start
log(f"  Completed in {elapsed:.1f}s: {output.strip()}")

# Step 4: Gather results
log(f"\n{'='*60}")
log("INDIVIDUAL RESULTS")
log(f"{'='*60}")
successes = 0
for i in range(NUM_REQUESTS):
    if not session_ids[i]:
        log(f"  — Request #{i}: SKIPPED (no session)")
        continue
    _, o, _ = c.exec_command(f"cat /tmp/stress_test/r{i}.json")
    body = o.read().decode().strip()
    try:
        data = json.loads(body)
        has_msg = "messages" in data and len(data["messages"]) > 0
        error = data.get("detail", None)
        ok = has_msg and not error
    except:
        ok = False
        error = body[:200]
        data = {}

    if ok:
        msg_count = len(data.get("messages", []))
        last_msg = data["messages"][-1].get("content", "")[:100]
        log(f"  ✓ #{i}: SUCCESS ({msg_count} msgs)")
        log(f"        Q: {QUESTIONS[i]}")
        log(f"        A: {last_msg}...")
        successes += 1
    else:
        if isinstance(error, str):
            log(f"  ✗ #{i}: FAIL — {error[:150]}")
        else:
            log(f"  ✗ #{i}: FAIL — {body[:150]}")

# Step 5: Backend log analysis
log(f"\n{'='*60}")
log("BACKEND LOG ANALYSIS")
log(f"{'='*60}")

_, o, _ = c.exec_command(
    f'cd /opt/5491NoteBook && docker compose logs open_notebook --no-log-prefix 2>&1 | '
    f'tail -n +{log_before} | grep -iE "RuntimeError|event.loop|cannot be called|Traceback|Exception" | '
    f'grep -v "INFO:" | grep -v "httpx" | grep -v "cssselect" | head -20'
)
log_errors = o.read().decode().strip()
if log_errors:
    log("⚠️ Errors found:")
    for line in log_errors.split("\n")[:15]:
        log(f"  {line.strip()}")
else:
    log("✅ No errors in backend logs!")

# Counts
_, o, _ = c.exec_command(f'cd /opt/5491NoteBook && docker compose logs open_notebook --no-log-prefix 2>&1 | tail -n +{log_before} | grep -ciE "RuntimeError|event.loop|cannot be called"')
evt_errors = int(o.read().decode().strip() or "0")

_, o, _ = c.exec_command(f'cd /opt/5491NoteBook && docker compose logs open_notebook --no-log-prefix 2>&1 | tail -n +{log_before} | grep -c "500"')
http_500 = int(o.read().decode().strip() or "0")

_, o, _ = c.exec_command(f'cd /opt/5491NoteBook && docker compose logs open_notebook --no-log-prefix 2>&1 | tail -n +{log_before} | grep -c "Traceback"')
tb_count = int(o.read().decode().strip() or "0")

# Summary
log(f"\n{'='*60}")
log("SUMMARY")
log(f"{'='*60}")
log(f"  Notebook: {NB_ID}")
log(f"  Endpoint: {API_BASE} (Cloudflare → Nginx → Next.js → FastAPI)")
log(f"  Chat requests:    {successes}/{NUM_REQUESTS} successful")
log(f"  Total time:       {elapsed:.1f}s")
log(f"  Event loop errors: {evt_errors}")
log(f"  HTTP 500 errors:   {http_500}")
log(f"  Tracebacks:        {tb_count}")

if successes == NUM_REQUESTS and evt_errors == 0:
    log(f"\n🎉 PERFECT PASS: All {NUM_REQUESTS} requests successful, zero errors!")
elif successes >= 8 and evt_errors == 0:
    log(f"\n✅ PASS: System is stable!")
else:
    log(f"\n❌ Issues detected")
log(f"{'='*60}")

with open(r'd:\temp_stress_test.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(report))

c.close()
print("Report written to d:\\temp_stress_test.txt")
