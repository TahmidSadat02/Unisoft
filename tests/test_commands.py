import io
import os
import sys
import tempfile
import unittest

from app.storage import load_notes, save_notes
from main import build_parser


class TestCLICommands(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory() # create a fresh dir
        self.file_path = os.path.join(self.temp_dir.name, "notes.json") 
        self.parser = build_parser()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run_cli(self, args_list):
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            args = self.parser.parse_args(args_list)
            if hasattr(args, "func"):
                args.func(args)
        finally:
            sys.stdout = old_stdout
        return captured_output.getvalue()

    def test_add_first_note(self):
        output = self._run_cli(["--file", self.file_path, "add", "Buy groceries"])
        self.assertEqual(output.strip(), "Added note 1: Buy groceries")

        notes = load_notes(self.file_path)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0], {"id": 1, "text": "Buy groceries"})

    def test_add_multiple_notes(self):
        output1 = self._run_cli(["--file", self.file_path, "add", "First note"])
        output2 = self._run_cli(["--file", self.file_path, "add", "Second note"])

        self.assertEqual(output1.strip(), "Added note 1: First note")
        self.assertEqual(output2.strip(), "Added note 2: Second note")

        notes = load_notes(self.file_path)
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0], {"id": 1, "text": "First note"})
        self.assertEqual(notes[1], {"id": 2, "text": "Second note"})

    def test_list_empty(self):
        output = self._run_cli(["--file", self.file_path, "list"])
        self.assertEqual(output.strip(), "No notes found.")

    def test_list_multiple_notes(self):
        save_notes(
            self.file_path,
            [
                {"id": 1, "text": "First note"},
                {"id": 2, "text": "Second note"},
            ],
        )

        output = self._run_cli(["--file", self.file_path, "list"])
        lines = output.strip().splitlines()
        self.assertEqual(lines, ["1: First note", "2: Second note"])


if __name__ == "__main__":
    unittest.main()
