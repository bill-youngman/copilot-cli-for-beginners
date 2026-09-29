import sys
from typing import List, Optional

from books import Book, BookCollection


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
        print(f"\nError: {e}\n")


def handle_remove(collection: BookCollection) -> None:
    print("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()
    if not title:
        print("\nError: Title cannot be empty.\n")
        return

    collection.remove_book(title)

    print("\nBook removed if it existed.\n")


def handle_mark_read(collection: BookCollection) -> None:
    print("\nMark a Book as Read\n")

    title = input("Enter the title of the book to mark as read: ").strip()
    if not title:
        print("\nError: Title cannot be empty.\n")
        return

    book = collection.find_book_by_title(title)
    if book is None:
        print(f"\nError: No book found with the title '{title}'.\n")
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
        print("\nError: Author cannot be empty.\n")
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


def show_help() -> None:
    print("""
Book Collection Helper

Commands:
  list       - Show all books
  add        - Add a new book
  remove     - Remove a book by title
  find       - Find books by author
  search     - Search by title/author with an optional read-status filter
  mark-read  - Mark a book as read
  help       - Show this help message
""")


def main() -> None:
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()
    collection = BookCollection()

    if command == "list":
        handle_list(collection)
    elif command == "add":
        handle_add(collection)
    elif command == "remove":
        handle_remove(collection)
    elif command == "find":
        handle_find(collection)
    elif command == "search":
        handle_search(collection)
    elif command == "mark-read":
        handle_mark_read(collection)
    elif command == "help":
        show_help()
    else:
        print("Unknown command.\n")
        show_help()


if __name__ == "__main__":
    main()
