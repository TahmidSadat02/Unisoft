import argparse
import sys
from app.storage import load_notes, save_notes, file_lock, NotesFileCorruptedError  # Import storage functions, lock manager, and custom error

DEFAULT_NOTES_FILE = "notes.json"


def safe_execute(func, args) -> bool:
    """Wrapper to execute CLI command functions while catching file/IO/corruption errors gracefully."""
    try:
        func(args)  # Execute the subcommand handler (e.g. handle_add, handle_list)
        return True  # Command completed without errors
    except (NotesFileCorruptedError, PermissionError, OSError) as e:
        # Catch JSON corruption or file permission/IO errors, print clean error message to stderr without stack trace
        print(f"Error: {e}", file=sys.stderr)
        return False  # Indicate that command execution failed due to an error


def handle_not_implemented(args):
    print("not implemented")


def handle_add(args):
    # Acquire exclusive file lock before reading and writing to prevent concurrent race conditions (Attack 8)
    with file_lock(args.file):
        notes = load_notes(args.file)  # Load existing notes under lock
        next_id = max([n.get("id", 0) for n in notes], default=0) + 1  # Calculate next unique note ID
        new_note = {"id": next_id, "text": args.text}  # Construct new note object
        notes.append(new_note)  # Append new note to list
        save_notes(args.file, notes)  # Write updated notes list back to disk under lock
        print(f"Added note {next_id}: {args.text}")  # Output confirmation message


def handle_list(args):
    notes = load_notes(args.file)
    if not notes:
        print("No notes found.")
        return
    for note in notes:
        print(f"{note['id']}: {note['text']}")


def handle_search(args):
    notes = load_notes(args.file)
    query = args.query.lower()
    matches = [note for note in notes if query in note.get("text", "").lower()]
    if not matches:
        print("No matching notes found.")
        return
    for note in matches:
        print(f"{note['id']}: {note['text']}")


def handle_delete(args):
    # Acquire exclusive file lock before reading and modifying notes storage (Attack 8)
    with file_lock(args.file):
        notes = load_notes(args.file)  # Load existing notes under lock
        if not notes:
            print("No notes found.")
            return

        target = args.target
        target_note = None

        if target.isdigit():
            target_id = int(target)
            target_note = next((n for n in notes if n.get("id") == target_id), None)

        if target_note is None:
            matches = [n for n in notes if target.lower() in n.get("text", "").lower()]
            if not matches:
                print("Note not found.")
                return
            elif len(matches) > 1:
                print("Multiple notes matched. Please specify a unique note ID:")
                for n in matches:
                    print(f"{n['id']}: {n['text']}")
                return
            else:
                target_note = matches[0]

        confirm = input(
            f'Are you sure you want to delete note {target_note["id"]} ("{target_note["text"]}")? (y/n): '
        ).strip().lower()

        if confirm in ["y", "yes"]:
            remaining_notes = [n for n in notes if n.get("id") != target_note["id"]]
            save_notes(args.file, remaining_notes)  # Save modified notes under lock
            print(f"Note {target_note['id']} deleted.")
        else:
            print("Deletion cancelled.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI Application")
    parser.add_argument(
        "--file",
        default=DEFAULT_NOTES_FILE,
        help="Path to notes storage JSON file",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Add subcommand
    add_parser = subparsers.add_parser("add", help="Add a new note")
    add_parser.add_argument("text", type=str, help="Text content of the note")
    add_parser.set_defaults(func=handle_add)

    # List subcommand
    list_parser = subparsers.add_parser("list", help="List all notes")
    list_parser.set_defaults(func=handle_list)

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Search notes")
    search_parser.add_argument("query", type=str, help="Search query string")
    search_parser.set_defaults(func=handle_search)

    # Delete subcommand
    delete_parser = subparsers.add_parser("delete", help="Delete a note")
    delete_parser.add_argument("target", type=str, help="Note ID or search string")
    delete_parser.set_defaults(func=handle_delete)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        # Safely execute subcommand via safe_execute wrapper to handle errors cleanly
        if not safe_execute(args.func, args):
            sys.exit(1)  # Exit with status code 1 on caught file/storage errors
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
