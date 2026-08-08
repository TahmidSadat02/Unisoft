import json
import os
from typing import List, Dict, Any
from contextlib import contextmanager  # Import contextmanager helper to build custom 'with' statement lock contexts

# Safely attempt to import fcntl for POSIX file locking (macOS/Linux)
try:
    import fcntl  # Provides system-level file locking (flock) to prevent concurrent write race conditions
except ImportError:
    fcntl = None  # Fallback to None on platforms (like Windows) where fcntl module is unavailable


class NotesFileCorruptedError(Exception):
    """Raised when the notes file exists but contains invalid JSON."""
    pass


@contextmanager
def file_lock(path: str):
    """Context manager for acquiring an exclusive file lock on path.lock to prevent race conditions."""
    # If fcntl module is not supported on this OS, yield control without locking
    if fcntl is None:
        yield
        return

    # Derive dedicated lock file path (e.g. notes.json.lock) to avoid interfering with data file
    lock_path = path + ".lock"

    # Ensure parent directory for the lock file exists before opening
    dirname = os.path.dirname(lock_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    # Open the lock file in write mode to get a valid file descriptor
    with open(lock_path, "w") as f:
        # Acquire exclusive lock (LOCK_EX); blocks other processes until this lock is released
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            # Yield control back to the caller executing inside the 'with file_lock(...):' block
            yield
        finally:
            # Unlock file (LOCK_UN) when exiting context, allowing other processes to proceed safely
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def load_notes(path: str) -> List[Dict[str, Any]]:
    """
    Loads notes from a JSON file specified by path.
    Returns an empty list if the file does not exist or is empty.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        raise NotesFileCorruptedError(
            f"{path} contains invalid JSON and could not be read: {e}"
        )


def save_notes(path: str, notes: List[Dict[str, Any]]) -> None:
    """
    Saves a list of note dictionaries to a JSON file at path.
    Creates parent directories if necessary.
    """
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)
