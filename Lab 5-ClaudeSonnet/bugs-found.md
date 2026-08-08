
## Attack 1 — Add a note with an empty body
No issues, Perfectly Done.

---

## Attack 2 — Add a note 100,000 characters long
No issue, Successfully done.

---

## Attack 3 — Add a note containing emoji and Bengali text
**What I did:** Ran `python main.py --file test.json add "আজকের নোট 😃📝"` and listed the notes.
**Did the existing tests catch this?** No. Existing tests only used ASCII English characters.

---

## Attack 4 — Delete a note that does not exist
**What I did:** Ran `python main.py --file test.json delete 999` against a storage file.
**Did the existing tests catch this?** Yes. `test_commands.py` contains `test_delete_note_not_found` which tests deleting non-existent IDs.

---

## Attack 5 — Search with a regex special character like .*
**What I did:** Ran `python main.py --file test.json search ".*"` on a storage file with notes.
Output `No matching notes found.` because the search implementation uses Python's string `in` operator (`query in note['text']`), treating `.*` as a plain string literal rather than a regex expression.
**Did the existing tests catch this?** No. Existing tests searched with plain alphanumeric keywords (`"buy"`, `"DOCTOR"`).

---

## Attack 6 — Corrupt the JSON file by hand, then run any command
**What I did:** Wrote invalid JSON content (`invalid json {{`) to `test.json` and ran `python main.py --file test.json list`.
**What happened:** The CLI crashed with an unhandled exception traceback: `app.storage.NotesFileCorruptedError: test.json contains invalid JSON and could not be read: Expecting value: line 1 column 1 (char 0)`.
**Root cause:** `app.storage.load_notes` raised custom `NotesFileCorruptedError` when JSON decoding failed, but `main.py` did not catch `NotesFileCorruptedError` during command execution.
**Severity:** Medium.
**Fix:** Introduced `safe_execute` in `main.py` to catch `NotesFileCorruptedError` (and other storage errors), print a user-friendly error message `Error: <message>` to `sys.stderr`, and exit with code 1.
**Regression test added:** Added `test_corrupted_json_handled` in `tests/test_commands.py`.
**Did the existing tests catch this?** No. Existing tests only checked missing and empty JSON files in `storage.py`, not corrupted JSON handling in CLI command execution.

---

## Attack 7 — Make the JSON file read-only, then add a note
**What I did:** Set file permissions of `test.json` to read-only (`chmod 444 test.json`) and ran `python main.py --file test.json add "New note"`.
**What happened:** The CLI crashed with an unhandled traceback: `PermissionError: [Errno 13] Permission denied: 'test.json'`.
**Root cause:** `app.storage.save_notes` attempted `open(path, "w")` without handling `PermissionError` or `OSError`, and `main.py` lacked top-level error handling for file I/O permissions.
**Fix:** Configured `safe_execute` in `main.py` to catch `PermissionError` and `OSError`, print `Error: [Errno 13] Permission denied: 'test.json'` to `sys.stderr`, and exit with code 1.
**Regression test added:** Added `test_readonly_file_handled` in `tests/test_commands.py`.
**Did the existing tests catch this?** No. Existing tests interacted with read-write temporary files.

---

## Attack 8 — Run two adds at the same time in two terminals
**What I did:** Executed two concurrent threads running `python main.py --file test.json add "Note A"` and `python main.py --file test.json add "Note B"` simultaneously on the same storage file.
**What happened:** A race condition occurred: both commands read the file concurrently, computed `id = 1`, and wrote to disk. The second process overwrote the first, resulting in data loss (only `Note B` remained; `Note A` was lost).
**Root cause:** `load_notes` and `save_notes` were un-locked operations in `handle_add` and `handle_delete`, leaving a window for race conditions during read-modify-write sequences across multiple processes.
**Severity:** High (Data Loss).
**Fix:** Implemented a POSIX file locking context manager `file_lock(path)` using `fcntl.flock` in `app/storage.py`, and wrapped `handle_add` and `handle_delete` operations in `main.py` with `with file_lock(args.file):` to atomically serialize concurrent writes.
**Regression test added:** Added `test_concurrent_adds` in `tests/test_storage.py`.
**Did the existing tests catch this?** No. Existing tests ran sequentially in a single thread.
