"""Tests for assertion types."""

import pytest

from promptlab.assertions import check_assertion


class TestContains:
    def test_pass(self):
        result = check_assertion({"type": "contains", "value": "hello"}, "Hello world", "")
        assert result["passed"] is True

    def test_fail(self):
        result = check_assertion({"type": "contains", "value": "goodbye"}, "Hello world", "")
        assert result["passed"] is False

    def test_case_insensitive(self):
        result = check_assertion({"type": "contains", "value": "HELLO"}, "hello world", "")
        assert result["passed"] is True


class TestNotContains:
    def test_pass(self):
        result = check_assertion({"type": "not_contains", "value": "error"}, "All good", "")
        assert result["passed"] is True

    def test_fail(self):
        result = check_assertion({"type": "not_contains", "value": "error"}, "An error occurred", "")
        assert result["passed"] is False


class TestStartsWith:
    def test_pass(self):
        result = check_assertion({"type": "starts_with", "value": "Sure"}, "Sure, I can help", "")
        assert result["passed"] is True

    def test_fail(self):
        result = check_assertion({"type": "starts_with", "value": "No"}, "Sure, I can help", "")
        assert result["passed"] is False

    def test_strips_whitespace(self):
        result = check_assertion({"type": "starts_with", "value": "Sure"}, "  Sure, I can help", "")
        assert result["passed"] is True


class TestRegex:
    def test_pass(self):
        result = check_assertion({"type": "regex", "value": r"\d{4}"}, "The year is 2026", "")
        assert result["passed"] is True

    def test_fail(self):
        result = check_assertion({"type": "regex", "value": r"\d{4}"}, "No numbers here", "")
        assert result["passed"] is False

    def test_invalid_regex(self):
        result = check_assertion({"type": "regex", "value": r"[invalid"}, "test", "")
        assert result["passed"] is False
        assert "Invalid regex" in result["message"]


class TestEquals:
    def test_pass(self):
        result = check_assertion({"type": "equals", "value": "42"}, "42", "")
        assert result["passed"] is True

    def test_fail(self):
        result = check_assertion({"type": "equals", "value": "42"}, "43", "")
        assert result["passed"] is False

    def test_strips_whitespace(self):
        result = check_assertion({"type": "equals", "value": "42"}, "  42  ", "")
        assert result["passed"] is True


class TestMaxTokens:
    def test_pass(self):
        result = check_assertion({"type": "max_tokens", "value": 10}, "Short response", "")
        assert result["passed"] is True

    def test_fail(self):
        long_text = " ".join(["word"] * 50)
        result = check_assertion({"type": "max_tokens", "value": 5}, long_text, "")
        assert result["passed"] is False


class TestMinLength:
    def test_pass(self):
        result = check_assertion({"type": "min_length", "value": 5}, "Hello world", "")
        assert result["passed"] is True

    def test_fail(self):
        result = check_assertion({"type": "min_length", "value": 100}, "Short", "")
        assert result["passed"] is False


class TestMaxLength:
    def test_pass(self):
        result = check_assertion({"type": "max_length", "value": 20}, "Short", "")
        assert result["passed"] is True

    def test_fail(self):
        result = check_assertion({"type": "max_length", "value": 3}, "This is too long", "")
        assert result["passed"] is False


class TestUnknownType:
    def test_unknown(self):
        result = check_assertion({"type": "nonexistent", "value": "x"}, "test", "")
        assert result["passed"] is False
        assert "Unknown assertion type" in result["message"]
