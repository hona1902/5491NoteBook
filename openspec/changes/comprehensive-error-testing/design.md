## Context

Following the implementation of the "fix-vps-performance-issues" change, the backend architecture for handling chat requests has fundamentally changed. The previous synchronous, blocking model was replaced with an asynchronous Server-Sent Events (SSE) streaming model. Additionally, SurrealDB connections are now managed via an application-level connection pool rather than opening a new connection per request. We need to computationally verify that these architectural changes resolve the Cloudflare 524 timeouts and prevent server hangs under concurrent load.

## Goals / Non-Goals

**Goals:**
- Create an automated test suite that can run from a local machine and target the remote VPS.
- Verify that the `/api/chat/stream` endpoint streams responses successfully without timing out.
- Verify that multiple simultaneous chat requests (e.g., 5-10 concurrent requests) are handled smoothly without degrading response time or locking up the database.
- Verify that the server successfully detects and cleans up resources when a client abruptly disconnects during an SSE stream.

**Non-Goals:**
- Full end-to-end integration testing using a headless browser (Puppeteer/Playwright).
- Load testing to the point of server failure (stress testing to breaking point). We only want to test real-world concurrent usage levels.

## Decisions

- Use Python's `asyncio` and `aiohttp` for the test requests to easily simulate concurrent connections.
- Use the `sseclient` library or manual chunk parsing to consume the SSE streams and measure latency between chunks.
- For disconnect testing, we will initiate an `aiohttp` request, read a few chunks, and then intentionally cancel the task (closing the TCP connection) and check the server logs (separately) to confirm the Disconnected exception was handled.

## Risks / Trade-offs

- **Risk**: The tests overwhelm the VPS during normal operation.
  - **Mitigation**: We will cap concurrency to a safe reasonable bound (e.g., 5-10 concurrent sessions), which simulates peak normal traffic rather than a DDoS attack.
