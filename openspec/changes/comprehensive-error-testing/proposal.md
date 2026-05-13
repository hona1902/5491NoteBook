## Why

We recently implemented significant architectural changes to address Cloudflare 524 timeouts and backend hangs on the VPS (`160.30.113.168`). These changes included SurrealDB connection pooling, SSE streaming endpoints, and client disconnect detection. To ensure these fixes are robust and no new regressions were introduced, we must run comprehensive testing covering all historical failure modes (concurrent load, streaming stability, client disconnects).

## What Changes

- Create automated stress tests using Python's `asyncio` and `aiohttp` to simulate concurrent user sessions.
- Implement tests verifying SSE stream reliability under load.
- Implement tests simulating sudden client disconnects (tab closures) to verify the backend correctly terminates the request without leaving zombie threads.
- Implement data consistency checks during concurrent writes.

## Capabilities

### New Capabilities
- `vps-performance-testing`: Create automated test suites capable of stress-testing the VPS endpoints including the new SSE streaming endpoints, verifying connection pooling, and simulating real-world concurrent usage patterns.

### Modified Capabilities
- (None)

## Impact

No production code changes. This will add new test scripts (`test_vps_comprehensive.py` or similar) and modify existing test utilities to support the new SSE streaming payload format.
