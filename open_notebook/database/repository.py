import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypeVar, Union

from loguru import logger
from surrealdb import AsyncSurreal, RecordID  # type: ignore

T = TypeVar("T", Dict[str, Any], List[Dict[str, Any]])


def get_database_url():
    """Get database URL with backward compatibility"""
    surreal_url = os.getenv("SURREAL_URL")
    if surreal_url:
        return surreal_url

    # Fallback to old format - WebSocket URL format
    address = os.getenv("SURREAL_ADDRESS", "localhost")
    port = os.getenv("SURREAL_PORT", "8000")
    return f"ws://{address}/rpc:{port}"


def get_database_password():
    """Get password with backward compatibility"""
    return os.getenv("SURREAL_PASSWORD") or os.getenv("SURREAL_PASS")


def parse_record_ids(obj: Any) -> Any:
    """Recursively parse and convert RecordIDs into strings."""
    if isinstance(obj, dict):
        return {k: parse_record_ids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [parse_record_ids(item) for item in obj]
    elif isinstance(obj, RecordID):
        return str(obj)
    return obj


def ensure_record_id(value: Union[str, RecordID]) -> RecordID:
    """Ensure a value is a RecordID."""
    if isinstance(value, RecordID):
        return value
    return RecordID.parse(value)


# ---------------------------------------------------------------------------
# SurrealDB Connection Pool
# ---------------------------------------------------------------------------

class SurrealConnectionPool:
    """Async connection pool for SurrealDB WebSocket connections.

    Maintains a pool of pre-authenticated AsyncSurreal connections to avoid
    the overhead (and handshake timeouts) of creating a new WebSocket
    connection for every database operation.
    """

    def __init__(self, max_size: int = 20):
        self._pool: asyncio.Queue[AsyncSurreal] = asyncio.Queue(maxsize=max_size)
        self._max_size = max_size
        self._current_size = 0
        self._lock = asyncio.Lock()

    async def _create_connection(self) -> AsyncSurreal:
        """Create a new authenticated SurrealDB connection."""
        db = AsyncSurreal(get_database_url())
        await db.signin(
            {
                "username": os.environ.get("SURREAL_USER"),
                "password": get_database_password(),
            }
        )
        await db.use(
            os.environ.get("SURREAL_NAMESPACE"), os.environ.get("SURREAL_DATABASE")
        )
        return db

    async def _health_check(self, conn: AsyncSurreal) -> bool:
        """Test whether a pooled connection is still alive."""
        try:
            # A lightweight query that verifies the connection works
            await conn.query("RETURN true")
            return True
        except Exception:
            return False

    async def acquire(self) -> AsyncSurreal:
        """Get a healthy connection from the pool (or create one)."""
        # 1. Try to grab an existing connection from the queue
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
            except asyncio.QueueEmpty:
                break

            # Validate before handing out
            if await self._health_check(conn):
                return conn

            # Stale — discard and decrement size
            async with self._lock:
                self._current_size -= 1
            try:
                await conn.close()
            except Exception:
                pass
            logger.debug("Discarded stale SurrealDB pool connection")

        # 2. Create a new connection if room remains
        async with self._lock:
            if self._current_size < self._max_size:
                self._current_size += 1
                try:
                    return await self._create_connection()
                except Exception:
                    self._current_size -= 1
                    raise

        # 3. Pool is full — wait for a connection to be returned
        conn = await self._pool.get()
        if await self._health_check(conn):
            return conn

        # Returned connection was stale — replace it
        async with self._lock:
            self._current_size -= 1
        try:
            await conn.close()
        except Exception:
            pass

        async with self._lock:
            self._current_size += 1
        try:
            return await self._create_connection()
        except Exception:
            async with self._lock:
                self._current_size -= 1
            raise

    async def release(self, conn: AsyncSurreal) -> None:
        """Return a connection to the pool."""
        try:
            self._pool.put_nowait(conn)
        except asyncio.QueueFull:
            # Pool is already full — close the surplus connection
            async with self._lock:
                self._current_size -= 1
            try:
                await conn.close()
            except Exception:
                pass


# Global pool singleton (lazy init)
_pool: Optional[SurrealConnectionPool] = None


async def get_pool() -> SurrealConnectionPool:
    """Return the global connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        max_size = int(os.getenv("SURREAL_POOL_SIZE", "20"))
        _pool = SurrealConnectionPool(max_size=max_size)
        logger.info(f"SurrealDB connection pool initialized (max_size={max_size})")
    return _pool


@asynccontextmanager
async def db_connection():
    """Async context manager that borrows a connection from the pool.

    API surface is unchanged — existing callers continue to work:
        async with db_connection() as conn:
            result = await conn.query(...)
    """
    pool = await get_pool()
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)


async def repo_query(
    query_str: str, vars: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Execute a SurrealQL query and return the results"""

    async with db_connection() as connection:
        try:
            result = parse_record_ids(await connection.query(query_str, vars))
            if isinstance(result, str):
                raise RuntimeError(result)
            return result
        except RuntimeError as e:
            # RuntimeError is raised for retriable transaction conflicts - log at debug to avoid noise
            logger.debug(str(e))
            raise
        except Exception as e:
            logger.exception(e)
            raise


async def repo_create(table: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new record in the specified table"""
    # Remove 'id' attribute if it exists in data
    data.pop("id", None)
    data["created"] = datetime.now(timezone.utc)
    data["updated"] = datetime.now(timezone.utc)
    try:
        async with db_connection() as connection:
            result = parse_record_ids(await connection.insert(table, data))
            # SurrealDB may return a string error message instead of the expected record
            if isinstance(result, str):
                raise RuntimeError(result)
            return result
    except RuntimeError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.exception(e)
        raise RuntimeError("Failed to create record")


async def repo_relate(
    source: str, relationship: str, target: str, data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Create a relationship between two records with optional data"""
    if data is None:
        data = {}
    query = f"RELATE {source}->{relationship}->{target} CONTENT $data;"
    # logger.debug(f"Relate query: {query}")

    return await repo_query(
        query,
        {
            "data": data,
        },
    )


async def repo_upsert(
    table: str, id: Optional[str], data: Dict[str, Any], add_timestamp: bool = False
) -> List[Dict[str, Any]]:
    """Create or update a record in the specified table"""
    data.pop("id", None)
    if add_timestamp:
        data["updated"] = datetime.now(timezone.utc)
    query = f"UPSERT {id if id else table} MERGE $data;"
    return await repo_query(query, {"data": data})


async def repo_update(
    table: str, id: str, data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Update an existing record by table and id"""
    # If id already contains the table name, use it as is
    try:
        if isinstance(id, RecordID) or (":" in id and id.startswith(f"{table}:")):
            record_id = id
        else:
            record_id = f"{table}:{id}"
        data.pop("id", None)
        if "created" in data and isinstance(data["created"], str):
            data["created"] = datetime.fromisoformat(data["created"])
        data["updated"] = datetime.now(timezone.utc)
        query = f"UPDATE {record_id} MERGE $data;"
        # logger.debug(f"Update query: {query}")
        result = await repo_query(query, {"data": data})
        # if isinstance(result, list):
        #     return [_return_data(item) for item in result]
        return parse_record_ids(result)
    except Exception as e:
        raise RuntimeError(f"Failed to update record: {str(e)}")


async def repo_delete(record_id: Union[str, RecordID]):
    """Delete a record by record id"""

    try:
        async with db_connection() as connection:
            return await connection.delete(ensure_record_id(record_id))
    except Exception as e:
        logger.exception(e)
        raise RuntimeError(f"Failed to delete record: {str(e)}")


async def repo_insert(
    table: str, data: List[Dict[str, Any]], ignore_duplicates: bool = False
) -> List[Dict[str, Any]]:
    """Create a new record in the specified table"""
    try:
        async with db_connection() as connection:
            result = parse_record_ids(await connection.insert(table, data))
            # SurrealDB may return a string error message instead of the expected records
            if isinstance(result, str):
                raise RuntimeError(result)
            return result
    except RuntimeError as e:
        if ignore_duplicates and "already contains" in str(e):
            return []
        # Log transaction conflicts at debug level (they are expected during concurrent operations)
        error_str = str(e).lower()
        if "transaction" in error_str or "conflict" in error_str:
            logger.debug(str(e))
        else:
            logger.error(str(e))
        raise
    except Exception as e:
        if ignore_duplicates and "already contains" in str(e):
            return []
        logger.exception(e)
        raise RuntimeError("Failed to create record")
