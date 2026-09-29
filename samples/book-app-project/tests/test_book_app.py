import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection
from book_app import validate_book_input, handle_add, handle_remove, handle_find, handle_mark_read, handle_search, parse_read_status


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


class TestValidateBookInput:
    def test_valid_input(self):
        title, author, year = validate_book_input("Dune", "Frank Herbert", "1965")
        assert title == "Dune"
        assert author == "Frank Herbert"
        assert year == 1965

    def test_empty_title_raises(self):
        with pytest.raises(ValueError, match="Title cannot be empty"):
            validate_book_input("", "Frank Herbert", "1965")

    def test_empty_author_raises(self):
        with pytest.raises(ValueError, match="Author cannot be empty"):
            validate_book_input("Dune", "", "1965")

    def test_empty_year_raises(self):
        with pytest.raises(ValueError, match="Year must be a positive whole number"):
            validate_book_input("Dune", "Frank Herbert", "")

    def test_non_numeric_year_raises(self):
        with pytest.raises(ValueError, match="Year must be a positive whole number"):
            validate_book_input("Dune", "Frank Herbert", "not-a-year")

    def test_zero_year_raises(self):
        with pytest.raises(ValueError, match="Year must be a positive whole number"):
            validate_book_input("Dune", "Frank Herbert", "0")

    def test_negative_year_raises(self):
        with pytest.raises(ValueError, match="Year must be a positive whole number"):
            validate_book_input("Dune", "Frank Herbert", "-1965")


class TestHandleAdd:
    def test_adds_valid_book(self, monkeypatch, capsys):
        collection = BookCollection()
        inputs = iter(["1984", "George Orwell", "1949"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        handle_add(collection)

        assert collection.find_book_by_title("1984") is not None
        assert "Book added successfully" in capsys.readouterr().out

    def test_rejects_invalid_year(self, monkeypatch, capsys):
        collection = BookCollection()
        inputs = iter(["1984", "George Orwell", "not-a-year"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        handle_add(collection)

        assert collection.find_book_by_title("1984") is None
        assert "Error" in capsys.readouterr().out


class TestHandleRemove:
    def test_rejects_empty_title(self, monkeypatch, capsys):
        collection = BookCollection()
        monkeypatch.setattr("builtins.input", lambda _: "")

        handle_remove(collection)

        assert "Title cannot be empty" in capsys.readouterr().out


class TestHandleFind:
    def test_rejects_empty_author(self, monkeypatch, capsys):
        collection = BookCollection()
        monkeypatch.setattr("builtins.input", lambda _: "")

        handle_find(collection)

        assert "Author cannot be empty" in capsys.readouterr().out

    def test_finds_books_by_author(self, monkeypatch, capsys):
        collection = BookCollection()
        collection.add_book("Dune", "Frank Herbert", 1965)
        monkeypatch.setattr("builtins.input", lambda _: "Frank Herbert")

        handle_find(collection)

        assert "Dune" in capsys.readouterr().out


class TestHandleMarkRead:
    def test_rejects_empty_title(self, monkeypatch, capsys):
        collection = BookCollection()
        monkeypatch.setattr("builtins.input", lambda _: "")

        handle_mark_read(collection)

        assert "Title cannot be empty" in capsys.readouterr().out

    def test_title_not_found(self, monkeypatch, capsys):
        collection = BookCollection()
        monkeypatch.setattr("builtins.input", lambda _: "Nonexistent Book")

        handle_mark_read(collection)

        assert "No book found" in capsys.readouterr().out

    def test_marks_unread_book_as_read(self, monkeypatch, capsys):
        collection = BookCollection()
        collection.add_book("Dune", "Frank Herbert", 1965)
        monkeypatch.setattr("builtins.input", lambda _: "Dune")

        handle_mark_read(collection)

        assert collection.find_book_by_title("Dune").read is True
        assert "marked as read" in capsys.readouterr().out

    def test_already_read_book_shows_friendly_note(self, monkeypatch, capsys):
        collection = BookCollection()
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.mark_as_read("Dune")
        monkeypatch.setattr("builtins.input", lambda _: "Dune")

        handle_mark_read(collection)

        assert collection.find_book_by_title("Dune").read is True
        assert "already marked as read" in capsys.readouterr().out


class TestParseReadStatus:
    def test_read_variants(self):
        assert parse_read_status("r") is True
        assert parse_read_status("Read") is True

    def test_unread_variants(self):
        assert parse_read_status("u") is False
        assert parse_read_status("Unread") is False

    def test_blank_or_unrecognized_defaults_to_all(self):
        assert parse_read_status("") is None
        assert parse_read_status("a") is None
        assert parse_read_status("all") is None
        assert parse_read_status("gibberish") is None


class TestHandleSearch:
    def _seed(self, collection: BookCollection) -> None:
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.add_book("1984", "George Orwell", 1949)
        collection.mark_as_read("Dune")

    def test_blank_query_and_status_returns_all(self, monkeypatch, capsys):
        collection = BookCollection()
        self._seed(collection)
        inputs = iter(["", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        handle_search(collection)

        out = capsys.readouterr().out
        assert "Dune" in out
        assert "1984" in out

    def test_text_query_narrows_results(self, monkeypatch, capsys):
        collection = BookCollection()
        self._seed(collection)
        inputs = iter(["dune", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        handle_search(collection)

        out = capsys.readouterr().out
        assert "Dune" in out
        assert "1984" not in out

    def test_status_filter_narrows_results(self, monkeypatch, capsys):
        collection = BookCollection()
        self._seed(collection)
        inputs = iter(["", "unread"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        handle_search(collection)

        out = capsys.readouterr().out
        assert "1984" in out
        assert "Dune" not in out

    def test_combined_filters(self, monkeypatch, capsys):
        collection = BookCollection()
        self._seed(collection)
        inputs = iter(["dune", "read"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        handle_search(collection)

        assert "Dune" in capsys.readouterr().out

    def test_invalid_status_defaults_to_all(self, monkeypatch, capsys):
        collection = BookCollection()
        self._seed(collection)
        inputs = iter(["", "not-a-status"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        handle_search(collection)

        out = capsys.readouterr().out
        assert "Dune" in out
        assert "1984" in out
