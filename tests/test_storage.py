import os
import tempfile
import unittest

from app.storage import load_notes, save_notes


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file(self):
        non_existent_path = os.path.join(self.temp_dir.name, "missing.json")
        result = load_notes(non_existent_path)
        self.assertEqual(result, [])

    def test_empty_file(self):
        empty_file_path = os.path.join(self.temp_dir.name, "empty.json")
        with open(empty_file_path, "w", encoding="utf-8") as f:
            f.write("")
        result = load_notes(empty_file_path)
        self.assertEqual(result, [])

    def test_one_note(self):
        note_file_path = os.path.join(self.temp_dir.name, "one_note.json")
        notes = [{"id": 1, "title": "First Note", "content": "Hello World"}]
        save_notes(note_file_path, notes)

        loaded_notes = load_notes(note_file_path)
        self.assertEqual(loaded_notes, notes)

    def test_roundtrip_three_notes(self):
        note_file_path = os.path.join(self.temp_dir.name, "three_notes.json")
        notes = [
            {"id": 1, "title": "Note 1", "content": "Content 1"},
            {"id": 2, "title": "Note 2", "content": "Content 2"},
            {"id": 3, "title": "Note 3", "content": "Content 3"},
        ]
        save_notes(note_file_path, notes)

        loaded_notes = load_notes(note_file_path)
        self.assertEqual(loaded_notes, notes)


if __name__ == "__main__":
    unittest.main()
