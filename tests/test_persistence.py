"""Transaction contracts independent of HTTP and actual music files."""
import sqlite3
import threading
import pytest
from backend import cancellation, persistence


@pytest.mark.parametrize('cancelled', [False, True])
def test_failed_or_cancelled_transaction_rolls_back_and_reopens(tmp_path, cancelled):
    store = persistence.SQLiteStore()
    event = threading.Event()
    with pytest.raises(cancellation.Cancelled if cancelled else RuntimeError):
        with cancellation.scope(event), store.transaction(tmp_path) as conn:
            conn.execute('INSERT INTO cache VALUES (?,?)', ('authored', '{}'))
            if cancelled:
                event.set()
            else:
                raise RuntimeError('authored failure')
    with store.transaction(tmp_path) as conn:
        assert conn.execute('SELECT * FROM cache').fetchall() == []
        conn.execute('INSERT INTO cache VALUES (?,?)', ('committed', '{}'))
    with store.transaction(tmp_path) as conn:
        assert conn.execute('SELECT key FROM cache').fetchall() == [('committed',)]
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute('SELECT 1')


def test_failed_recovery_remains_retryable(tmp_path, monkeypatch):
    store = persistence.SQLiteStore()
    calls = []
    def recover(data, conn):
        calls.append(data)
        if len(calls) == 1:
            conn.execute('INSERT INTO cache VALUES (?,?)', ('rolled-back', '{}'))
            raise RuntimeError('authored recovery failure')
    monkeypatch.setattr(persistence.storage, 'recover_deletions', recover)
    with pytest.raises(RuntimeError):
        with store.transaction(tmp_path):
            pass
    assert tmp_path.resolve() not in store.recovered_data
    with store.transaction(tmp_path) as conn:
        assert conn.execute('SELECT * FROM cache').fetchall() == []
    assert len(calls) == 2
