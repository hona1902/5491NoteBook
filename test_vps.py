import asyncio
import aiohttp
import time

BASE_URL = "https://sotay5491.io.vn/api/api"
NOTEBOOK_ID = "notebook:0iurid12q8ccdb53xve5"
NUM_SESSIONS = 10
MESSAGE = "Xin chào, hãy tóm tắt nội dung chính của notebook này."
PASSWORD = "HoaiNam190291"
AUTH_HEADERS = {"Authorization": f"Bearer {PASSWORD}"}

async def create_session(session: aiohttp.ClientSession, index: int):
    print(f"[{index}] Creating session...")
    async with session.post(f"{BASE_URL}/chat/sessions", json={"notebook_id": NOTEBOOK_ID}, headers=AUTH_HEADERS) as resp:
        if resp.status != 200:
            text = await resp.text()
            print(f"[{index}] Error creating session: {resp.status} - {text}")
            return None
        data = await resp.json()
        print(f"[{index}] Session created: {data['id']}")
        return data['id']

async def get_context(session: aiohttp.ClientSession, index: int):
    print(f"[{index}] Getting context...")
    async with session.post(f"{BASE_URL}/chat/context", json={"notebook_id": NOTEBOOK_ID, "context_config": {}}, headers=AUTH_HEADERS) as resp:
        if resp.status != 200:
            text = await resp.text()
            print(f"[{index}] Error getting context: {resp.status} - {text}")
            return {}
        data = await resp.json()
        return data.get('context', {})

async def execute_chat(session: aiohttp.ClientSession, session_id: str, context: dict, index: int):
    print(f"[{index}] Sending chat message...")
    start_time = time.time()
    payload = {
        "session_id": session_id,
        "message": MESSAGE,
        "context": context
    }
    
    # Increase timeout since it's a generation task
    timeout = aiohttp.ClientTimeout(total=300)
    try:
        async with session.post(f"{BASE_URL}/chat/execute", json=payload, headers=AUTH_HEADERS, timeout=timeout) as resp:
            elapsed = time.time() - start_time
            if resp.status != 200:
                text = await resp.text()
                print(f"[{index}] Error in chat ({elapsed:.2f}s): {resp.status} - {text}")
                return False, elapsed
            else:
                data = await resp.json()
                print(f"[{index}] Success in {elapsed:.2f}s - Got {len(data.get('messages', []))} messages")
                return True, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[{index}] Exception in chat ({elapsed:.2f}s): {str(e)}")
        return False, elapsed

async def run_worker(session: aiohttp.ClientSession, index: int):
    session_id = await create_session(session, index)
    if not session_id:
        return None
    
    context = await get_context(session, index)
    
    success, elapsed = await execute_chat(session, session_id, context, index)
    return success, elapsed

async def main():
    print(f"Starting stress test: {NUM_SESSIONS} concurrent sessions sending to {BASE_URL}")
    print(f"Notebook ID: {NOTEBOOK_ID}")
    
    # Use larger connection limit
    connector = aiohttp.TCPConnector(limit=NUM_SESSIONS + 5)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [run_worker(session, i) for i in range(NUM_SESSIONS)]
        start_total = time.time()
        
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_total
        
        successes = [r for r in results if r and r[0]]
        fails = [r for r in results if r and not r[0]]
        
        print(f"\n" + "="*40)
        print(f"RESULTS SUMMARY")
        print(f"="*40)
        print(f"Total test time: {total_time:.2f}s")
        print(f"Successful requests: {len(successes)}/{NUM_SESSIONS}")
        print(f"Failed requests:     {len(fails)}/{NUM_SESSIONS}")
        
        if successes:
            avg_time = sum(r[1] for r in successes) / len(successes)
            max_time = max(r[1] for r in successes)
            min_time = min(r[1] for r in successes)
            print(f"Success Avg response time: {avg_time:.2f}s")
            print(f"Success Min response time: {min_time:.2f}s")
            print(f"Success Max response time: {max_time:.2f}s")
            
        if fails:
            print(f"Fail Avg time before error: {sum(r[1] for r in fails) / len(fails):.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
