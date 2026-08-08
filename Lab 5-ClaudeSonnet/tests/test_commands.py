import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from app.storage import load_notes, save_notes
from main import build_parser


class TestCLICommands(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()  # create a fresh dir
        self.file_path = os.path.join(self.temp_dir.name, "notes.json")
        self.parser = build_parser()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run_cli(self, args_list):
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr  # Save original stderr stream reference
        try:
            sys.stdout = captured_output  # Redirect stdout to captured buffer
            sys.stderr = captured_output  # Redirect stderr to captured buffer to capture Error: messages
            args = self.parser.parse_args(args_list)
            if hasattr(args, "func"):
                from main import safe_execute
                safe_execute(args.func, args)  # Execute handler via safe_execute to catch exceptions and format error output
        finally:
            sys.stdout = old_stdout  # Restore stdout
            sys.stderr = old_stderr  # Restore stderr
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

    def test_search_matching_notes(self):
        save_notes(
            self.file_path,
            [
                {"id": 1, "text": "Buy milk"},
                {"id": 2, "text": "Call doctor"},
                {"id": 3, "text": "Buy groceries"},
            ],
        )

        output = self._run_cli(["--file", self.file_path, "search", "buy"])
        lines = output.strip().splitlines()
        self.assertEqual(lines, ["1: Buy milk", "3: Buy groceries"])

    def test_search_case_insensitive(self):
        save_notes(
            self.file_path,
            [
                {"id": 1, "text": "Call doctor"},
            ],
        )

        output = self._run_cli(["--file", self.file_path, "search", "DOCTOR"])
        self.assertEqual(output.strip(), "1: Call doctor")

    def test_search_no_matches(self):
        save_notes(
            self.file_path,
            [
                {"id": 1, "text": "Buy milk"},
            ],
        )

        output = self._run_cli(["--file", self.file_path, "search", "nonexistent"])
        self.assertEqual(output.strip(), "No matching notes found.")

    def test_search_empty_storage(self):
        output = self._run_cli(["--file", self.file_path, "search", "test"])
        self.assertEqual(output.strip(), "No matching notes found.")

    @patch("builtins.input", return_value="y")
    def test_delete_by_id_confirmed(self, mock_input):
        save_notes(
            self.file_path,
            [
                {"id": 1, "text": "Buy milk"},
                {"id": 2, "text": "Call doctor"},
            ],
        )
        output = self._run_cli(["--file", self.file_path, "delete", "1"])
        self.assertIn("Note 1 deleted.", output)

        notes = load_notes(self.file_path)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["id"], 2)

    @patch("builtins.input", return_value="n")
    def test_delete_by_id_cancelled(self, mock_input):
        save_notes(
            self.file_path,
            [
                {"id": 1, "text": "Buy milk"},
            ],
        )
        output = self._run_cli(["--file", self.file_path, "delete", "1"])
        self.assertIn("Deletion cancelled.", output)

        notes = load_notes(self.file_path)
        self.assertEqual(len(notes), 1)

    @patch("builtins.input", return_value="yes")
    def test_delete_by_search_string(self, mock_input):
        save_notes(
            self.file_path,
            [
                {"id": 1, "text": "Buy milk"},
                {"id": 2, "text": "Call doctor"},
            ],
        )
        output = self._run_cli(["--file", self.file_path, "delete", "doctor"])
        self.assertIn("Note 2 deleted.", output)

        notes = load_notes(self.file_path)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["id"], 1)

    def test_delete_note_not_found(self):
        save_notes(
            self.file_path,
            [
                {"id": 1, "text": "Buy milk"},
            ],
        )
        output = self._run_cli(["--file", self.file_path, "delete", "99"])
        self.assertEqual(output.strip(), "Note not found.")

    def test_delete_multiple_matches_requires_id(self):
        save_notes(
            self.file_path,
            [
                {"id": 1, "text": "Buy milk"},
                {"id": 2, "text": "Buy groceries"},
            ],
        )
        output = self._run_cli(["--file", self.file_path, "delete", "buy"])
        self.assertIn("Multiple notes matched. Please specify a unique note ID:", output)

    def test_corrupted_json_handled(self):  # Regression test for Attack 6 (Corrupted JSON file)
        # Write invalid JSON content to the notes file to simulate file corruption
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("invalid json {{")

        # Execute list subcommand against corrupted file
        output = self._run_cli(["--file", self.file_path, "list"])
        # Verify CLI handles corruption gracefully by outputting a clean Error: message without an unhandled traceback
        self.assertIn("Error:", output)

    def test_readonly_file_handled(self):  # Regression test for Attack 7 (Read-only file)
        # Initialize storage file with valid notes
        save_notes(self.file_path, [{"id": 1, "text": "Initial"}])
        # Set file permissions to read-only (0o444)
        os.chmod(self.file_path, 0o444)
        try:
            # Attempt to add a new note to read-only file
            output = self._run_cli(["--file", self.file_path, "add", "New note"])
            # Verify CLI outputs a clean Error: message instead of crashing with an unhandled PermissionError
            self.assertIn("Error:", output)
        finally:
            # Restore write permissions so cleanup works properly in tearDown
            os.chmod(self.file_path, 0o644)


if __name__ == "__main__":
    unittest.main()
