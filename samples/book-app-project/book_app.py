import sys
from typing import Callable, Dict, List, Optional

from books import Book, BookCollection


def print_error(message: str) -> None:
    """Print a consistently formatted error message."""
    print(f"\nError: {message}\n")


def show_books(books: List[Book]) -> None:
    """Display books in a user-friendly format."""
    if not books:
        print("No books found.")
        return

    print("\nYour Book Collection:\n")

    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")

    print()


def validate_book_input(title: str, author: str, year_str: str) -> tuple[str, str, int]:
    """Validate raw user input for a new book and return normalized values.

    Raises:
        ValueError: If the title/author is empty or the year is not a
            valid positive integer.
    """
    if not title:
        raise ValueError("Title cannot be empty.")
    if not author:
        raise ValueError("Author cannot be empty.")
    if not year_str.isdigit() or int(year_str) <= 0:
        raise ValueError("Year must be a positive whole number, e.g. 2024.")

    return title, author, int(year_str)


def handle_list(collection: BookCollection) -> None:
    books = collection.list_books()
    show_books(books)


def handle_add(collection: BookCollection) -> None:
    print("\nAdd a New Book\n")

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    year_str = input("Year: ").strip()

    try:
        title, author, year = validate_book_input(title, author, year_str)
        collection.add_book(title, author, year)
        print("\nBook added successfully.\n")
    except ValueError as e:
        print_error(str(e))


def handle_remove(collection: BookCollection) -> None:
    print("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()
    if not title:
        print_error("Title cannot be empty.")
        return

    if collection.remove_book(title):
        print(f"\n'{title}' removed.\n")
    else:
        print_error(f"No book found with the title '{title}'.")


def handle_mark_read(collection: BookCollection) -> None:
    print("\nMark a Book as Read\n")

    title = input("Enter the title of the book to mark as read: ").strip()
    if not title:
        print_error("Title cannot be empty.")
        return

    book = collection.find_book_by_title(title)
    if book is None:
        print_error(f"No book found with the title '{title}'.")
        return

    if book.read:
        print(f"\n'{book.title}' is already marked as read.\n")
        return

    collection.mark_as_read(title)
    print(f"\n'{book.title}' marked as read.\n")


def handle_find(collection: BookCollection) -> None:
    print("\nFind Books by Author\n")

    author = input("Author name: ").strip()
    if not author:
        print_error("Author cannot be empty.")
        return

    books = collection.find_by_author(author)
    show_books(books)


def parse_read_status(raw: str) -> Optional[bool]:
    """Map a status prompt answer to a read-status filter.

    Returns ``True`` for "read"/"r", ``False`` for "unread"/"u", and
    ``None`` (meaning "all") for anything else, including blank input.
    """
    normalized = raw.strip().lower()
    if normalized in ("r", "read"):
        return True
    if normalized in ("u", "unread"):
        return False
    return None


def handle_search(collection: BookCollection) -> None:
    print("\nSearch Books\n")

    query = input("Search text (title or author, leave blank for all): ").strip()
    status_input = input(
        "Filter by status - [a]ll / [r]ead / [u]nread (default: all): "
    ).strip()
    read_status = parse_read_status(status_input)

    books = collection.search_books(query, read_status)
    show_books(books)


COMMANDS: Dict[str, Callable[[BookCollection], None]] = {}
COMMAND_DESCRIPTIONS: Dict[str, str] = {
    "list": "Show all books",
    "add": "Add a new book",
    "remove": "Remove a book by title",
    "find": "Find books by author",
    "search": "Search by title/author with an optional read-status filter",
    "mark-read": "Mark a book as read",
}


def show_help() -> None:
    print("\nBook Collection Helper\n\nCommands:")
    width = max(len(name) for name in COMMAND_DESCRIPTIONS)
    for name, description in COMMAND_DESCRIPTIONS.items():
        print(f"  {name.ljust(width)}  - {description}")
    print(f"  {'help'.ljust(width)}  - Show this help message\n")


def main() -> None:
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if len(sys.argv) > 2:
        print(f"Note: ignoring extra arguments: {' '.join(sys.argv[2:])}\n")

    if command == "help":
        show_help()
        return

    handler = COMMANDS.get(command)
    if handler is None:
        print("Unknown command.\n")
        show_help()
        return

    collection = BookCollection()
    try:
        handler(collection)
    except OSError as e:
        print_error(f"Could not read or write the data file: {e}")


COMMANDS.update(
    {
        "list": handle_list,
        "add": handle_add,
        "remove": handle_remove,
        "find": handle_find,
        "search": handle_search,
        "mark-read": handle_mark_read,
    }
)


if __name__ == "__main__":
    main()
