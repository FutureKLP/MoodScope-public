"""SQLite connection lifecycle and transaction boundary for the local library.

Domain queries still use SQLite SQL. A future provider must preserve atomic
cache invalidation and deletion recovery, rather than swapping connection URLs.
"""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import threading

from . import cancellation, storage


class SQLiteStore:
    def __init__(self):
        self._init_lock = threading.RLock()
        self.recovered_data = set()

    @contextmanager
    def transaction(self, data):
        data = Path(data)
        conn = sqlite3.connect(data / 'cache.sqlite3', timeout=30)
        try:
            with self._init_lock:
                conn.execute('CREATE TABLE IF NOT EXISTS tracks (id TEXT PRIMARY KEY, metadata TEXT NOT NULL)')
                conn.execute('CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, result TEXT NOT NULL)')
                conn.execute('CREATE TABLE IF NOT EXISTS cache_owner (key TEXT PRIMARY KEY, track_id TEXT NOT NULL)')
                conn.execute('CREATE TABLE IF NOT EXISTS cache_state (name TEXT PRIMARY KEY, revision INTEGER NOT NULL)')
                root = data.resolve()
                if root not in self.recovered_data:
                    with conn:
                        conn.execute('BEGIN IMMEDIATE')
                        storage.recover_deletions(data, conn)
                    self.recovered_data.add(root)
            with conn:
                cancellation.check()
                yield conn
                cancellation.check()
        finally:
            conn.close()
