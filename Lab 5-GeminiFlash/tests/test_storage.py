import os
import tempfile
import unittest

from app.storage import load_notes, save_notes


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file(self):  # test file that doesn't exist
        non_existent_path = os.path.join(self.temp_dir.name, "missing.json")
        result = load_notes(non_existent_path)
        self.assertEqual(result, [])

    def test_empty_file(self):  # test file that is empty
        empty_file_path = os.path.join(self.temp_dir.name, "empty.json")
        with open(empty_file_path, "w", encoding="utf-8") as f:
            f.write("")
        result = load_notes(empty_file_path)
        self.assertEqual(result, [])

    def test_one_note(self):  # test file with one fake note
        note_file_path = os.path.join(self.temp_dir.name, "one_note.json")
        notes = [{"id": 1, "title": "First Note", "content": "Hello World"}]
        save_notes(note_file_path, notes)

        loaded_notes = load_notes(note_file_path)
        self.assertEqual(loaded_notes, notes)

    def test_roundtrip_three_notes(self):  # test file with multiple notes
        note_file_path = os.path.join(self.temp_dir.name, "three_notes.json")
        notes = [
            {"id": 1, "title": "Note 1", "content": "Content 1"},
            {"id": 2, "title": "Note 2", "content": "Content 2"},
            {"id": 3, "title": "Note 3", "content": "Content 3"},
        ]
        save_notes(note_file_path, notes)

        loaded_notes = load_notes(note_file_path)
        self.assertEqual(loaded_notes, notes)

    def test_concurrent_adds(self):  # Regression test for Attack 8 (Concurrent adds race condition)
        import subprocess
        import threading
        # Define temporary storage file path for testing concurrent writes
        note_file_path = os.path.join(self.temp_dir.name, "concurrent_notes.json")
        # Resolve absolute path to main.py CLI script
        main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))

        # Worker function to execute CLI add subcommand in a separate subprocess
        def add_worker(text):
            subprocess.run(["python3", main_py, "--file", note_file_path, "add", text], check=True)

        # Spawn two concurrent threads attempting to write notes simultaneously to the same file
        t1 = threading.Thread(target=add_worker, args=("Concurrent Note 1",))
        t2 = threading.Thread(target=add_worker, args=("Concurrent Note 2",))
        t1.start()  # Launch thread 1
        t2.start()  # Launch thread 2
        t1.join()   # Wait for thread 1 to complete execution
        t2.join()   # Wait for thread 2 to complete execution

        # Load saved notes from JSON file
        notes = load_notes(note_file_path)
        # Assert both notes were saved without data loss due to file locking (len == 2)
        self.assertEqual(len(notes), 2)


if __name__ == "__main__":
    unittest.main()
