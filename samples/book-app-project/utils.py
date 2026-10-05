from typing import List, Tuple

from books import Book


def print_menu() -> None:
    print("\n📚 Book Collection App")
    print("1. Add a book")
    print("2. List books")
    print("3. Mark book as read")
    print("4. Remove a book")
    print("5. Exit")


VALID_CHOICES = {"1", "2", "3", "4", "5"}


def get_user_choice() -> str:
    """Keep prompting until the user enters a valid menu option (1-5)."""
    while True:
        choice = input("Choose an option (1-5): ").strip()

        if not choice:
            print("No input entered. Please enter a number from 1 to 5.")
            continue

        if not choice.isdigit() or choice not in VALID_CHOICES:
            print(f"'{choice}' is not a valid option. Please enter a number from 1 to 5.")
            continue

        return choice


def get_book_details() -> Tuple[str, str, int]:
    """Prompt the user for details of a new book and return the parsed values.

    Prompts (in order):
        - Book title: re-prompts until a non-empty value is entered.
        - Author: re-prompts until a non-empty value is entered.
        - Publication year: parsed as an integer. If the input is not a
          valid whole number, a warning is printed and the year defaults
          to ``0`` instead of re-prompting.

    Returns:
        Tuple[str, str, int]: A ``(title, author, year)`` tuple, where
        ``title`` and ``author`` are guaranteed non-empty strings and
        ``year`` is an ``int`` (``0`` if the user's input wasn't a valid
        whole number).
    """
    title = _get_required_text("Enter book title: ")
    author = _get_required_text("Enter author: ")

    year_input = input("Enter publication year: ").strip()
    try:
        year = int(year_input)
    except ValueError:
        print("Invalid year. Defaulting to 0.")
        year = 0

    return title, author, year


def _get_required_text(prompt: str) -> str:
    """Keep prompting until the user provides a non-empty value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def print_books(books: List[Book]) -> None:
    if not books:
        print("No books in your collection.")
        return

    print("\nYour Books:")
    for index, book in enumerate(books, start=1):
        status = "✅ Read" if book.read else "📖 Unread"
        print(f"{index}. {book.title} by {book.author} ({book.year}) - {status}")
