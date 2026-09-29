import json
from dataclasses import dataclass, asdict
from typing import List, Optional

DATA_FILE = "data.json"


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False


@dataclass
class BookStatistics:
    total: int
    read: int
    unread: int
    oldest: Optional[Book]
    newest: Optional[Book]


def get_book_statistics(books: List[Book]) -> BookStatistics:
    """Compute summary statistics for a list of books.

    Args:
        books: The books to summarize.

    Returns:
        A BookStatistics with the total count, read/unread counts, and the
        oldest/newest book by publication year. ``oldest``/``newest`` are
        ``None`` when ``books`` is empty.
    """
    total = len(books)
    read_count = sum(1 for b in books if b.read)

    oldest = min(books, key=lambda b: b.year) if books else None
    newest = max(books, key=lambda b: b.year) if books else None

    return BookStatistics(
        total=total,
        read=read_count,
        unread=total - read_count,
        oldest=oldest,
        newest=newest,
    )


class BookCollection:
    def __init__(self):
        self.books: List[Book] = []
        self.load_books()

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")
            self.books = []

    def save_books(self):
        """Save the current book collection to JSON."""
        with open(DATA_FILE, "w") as f:
            json.dump([asdict(b) for b in self.books], f, indent=2)

    def add_book(self, title: str, author: str, year: int) -> Book:
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book by title."""
        book = self.find_book_by_title(title)
        if book:
            self.books.remove(book)
            self.save_books()
            return True
        return False

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author."""
        return [b for b in self.books if b.author.lower() == author.lower()]

    def search_books(
        self, query: str = "", read_status: Optional[bool] = None
    ) -> List[Book]:
        """Search books by a free-text query matched against title/author.

        Args:
            query: Case-insensitive substring matched against the title or
                author. An empty string matches every book.
            read_status: If not ``None``, further filter to books whose
                ``read`` flag equals this value.

        Returns:
            Books matching the query (if any) and the read-status filter
            (if any). Both filters combine with AND semantics.
        """
        normalized_query = query.strip().lower()

        results = self.books
        if normalized_query:
            results = [
                b
                for b in results
                if normalized_query in b.title.lower()
                or normalized_query in b.author.lower()
            ]

        if read_status is not None:
            results = [b for b in results if b.read == read_status]

        return results
