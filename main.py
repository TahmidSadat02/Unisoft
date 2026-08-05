import argparse
import sys


def handle_not_implemented(args):
    print("not implemented")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI Application")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Add subcommand
    add_parser = subparsers.add_parser("add", help="Add a new item")
    add_parser.set_defaults(func=handle_not_implemented)

    # List subcommand
    list_parser = subparsers.add_parser("list", help="List all items")
    list_parser.set_defaults(func=handle_not_implemented)

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Search items")
    search_parser.set_defaults(func=handle_not_implemented)

    # Delete subcommand
    delete_parser = subparsers.add_parser("delete", help="Delete an item")
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
