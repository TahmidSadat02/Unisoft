import argparse
import sys
from app.storage import load_notes, save_notes  # load notes from json file and save notes to json file

DEFAULT_NOTES_FILE = "notes.json"  # default file path set to notes.json


def handle_not_implemented(args):
    print("not implemented")


def handle_add(args):
    notes = load_notes(args.file)  # reads existing notes, take the list of notes
    next_id = max([n.get("id", 0) for n in notes], default=0) + 1  # add unique ID for each note, if no notes found then start from 1
    new_note = {"id": next_id, "text": args.text}  # create a new note with that unique ID
    notes.append(new_note)
    save_notes(args.file, notes)  # save notes to json file
    print(f"Added note {next_id}: {args.text}")  # prints the new note with the unique ID


def handle_list(args):
    notes = load_notes(args.file)  # read existing notes from json file
    if not notes:  # if no notes found
        print("No notes found.")
        return
    for note in notes:
        print(f"{note['id']}: {note['text']}")  # prints the unique ID and the text


def handle_search(args):
    notes = load_notes(args.file)  # read existing notes from json file
    query = args.query.lower()
    matches = [note for note in notes if query in note.get("text", "").lower()]
    if not matches:
        print("No matching notes found.")
        return
    for note in matches:
        print(f"{note['id']}: {note['text']}")


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
    delete_parser.set_defaults(func=handle_not_implemented)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
