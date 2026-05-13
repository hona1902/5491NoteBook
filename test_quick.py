"""Quick single-request test to verify async fix works."""
import asyncio
import aiohttp
import json
import time

# Test via Cloudflare
BASE = "https://sotay5491.io.vn"
NOTEBOOK_ID = "notebook:0iurid12q8ccdb53xve5"
AUTH_PASSWORD = "hoainam190291"


async def test_single():
    headers = {"Authorization": f"Bearer {AUTH_PASSWORD}"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # 1. Check API is up
        print("1. API health check...")
        async with session.get(f"{BASE}/api/notebooks") as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print(f"   Found {len(data)} notebooks")
            else:
                text = await resp.text()
                print(f"   Error: {text[:200]}")
                return
        
        # 2. Create a chat session
        print("\n2. Creating chat session...")
        async with session.post(
            f"{BASE}/api/chat/sessions",
            json={"notebook_id": NOTEBOOK_ID, "title": "Async Test"},
        ) as resp:
            print(f"   Status: {resp.status}")
            text = await resp.text()
            print(f"   Body: {text[:500]}")
            if resp.status == 200:
                data = json.loads(text)
                session_id = data.get("id", "")
                print(f"   Session ID: {session_id}")
            else:
                print("   FAILED!")
                return
        
        # 3. Send a chat message via execute endpoint
        print("\n3. Sending chat message (this will test async graph)...")
        start = time.time()
        async with session.post(
            f"{BASE}/api/chat/execute",
            json={
                "session_id": session_id,
                "message": "Xin chào! Hãy trả lời ngắn gọn bằng 1 câu.",
                "notebook_id": NOTEBOOK_ID,
            },
            timeout=aiohttp.ClientTimeout(total=120),
        ) as resp:
            elapsed = time.time() - start
            print(f"   Status: {resp.status} (took {elapsed:.1f}s)")
            text = await resp.text()
            print(f"   Response: {text[:500]}")
        
        print("\n✓ ASYNC FIX TEST COMPLETE!")


asyncio.run(test_single())
