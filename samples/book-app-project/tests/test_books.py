import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import Book, BookCollection, get_book_statistics


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result is True
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False

def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result is True
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result is False


class TestSearchBooks:
    def _make_collection(self) -> BookCollection:
        collection = BookCollection()
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.add_book("1984", "George Orwell", 1949)
        collection.add_book("Duneland Tales", "Someone Else", 2001)
        collection.mark_as_read("Dune")
        return collection

    def test_empty_query_returns_all(self):
        collection = self._make_collection()
        results = collection.search_books()
        assert len(results) == 3

    def test_matches_title_case_insensitive_partial(self):
        collection = self._make_collection()
        results = collection.search_books("dune")
        titles = {b.title for b in results}
        assert titles == {"Dune", "Duneland Tales"}

    def test_matches_author_case_insensitive_partial(self):
        collection = self._make_collection()
        results = collection.search_books("orwell")
        assert [b.title for b in results] == ["1984"]

    def test_read_status_filter_only(self):
        collection = self._make_collection()
        read_results = collection.search_books(read_status=True)
        assert [b.title for b in read_results] == ["Dune"]

        unread_results = collection.search_books(read_status=False)
        assert {b.title for b in unread_results} == {"1984", "Duneland Tales"}

    def test_combined_query_and_status_filter(self):
        collection = self._make_collection()
        results = collection.search_books("dune", read_status=False)
        assert [b.title for b in results] == ["Duneland Tales"]

    def test_no_matches_returns_empty_list(self):
        collection = self._make_collection()
        results = collection.search_books("nonexistent")
        assert results == []


class TestGetBookStatistics:
    def test_empty_list(self):
        stats = get_book_statistics([])
        assert stats.total == 0
        assert stats.read == 0
        assert stats.unread == 0
        assert stats.oldest is None
        assert stats.newest is None

    def test_mixed_read_and_unread(self):
        books_list = [
            Book(title="Dune", author="Frank Herbert", year=1965, read=True),
            Book(title="1984", author="George Orwell", year=1949, read=False),
            Book(title="The Hobbit", author="J.R.R. Tolkien", year=1937, read=True),
        ]

        stats = get_book_statistics(books_list)

        assert stats.total == 3
        assert stats.read == 2
        assert stats.unread == 1
        assert stats.oldest.title == "The Hobbit"
        assert stats.newest.title == "Dune"

    def test_single_book(self):
        books_list = [Book(title="Dune", author="Frank Herbert", year=1965)]

        stats = get_book_statistics(books_list)

        assert stats.total == 1
        assert stats.oldest is stats.newest is books_list[0]
