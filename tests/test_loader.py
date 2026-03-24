"""Tests for the YAML loader."""

import pytest
import tempfile
from pathlib import Path

from promptlab.loader import load_test_files, render_prompt


class TestRenderPrompt:
    def test_basic_render(self):
        template = "Hello {{ name }}, you are {{ age }} years old."
        result = render_prompt(template, {"name": "Alice", "age": "30"})
        assert result == "Hello Alice, you are 30 years old."

    def test_no_spaces(self):
        template = "Hello {{name}}"
        result = render_prompt(template, {"name": "Bob"})
        assert result == "Hello Bob"

    def test_no_variables(self):
        template = "No variables here"
        result = render_prompt(template, {})
        assert result == "No variables here"

    def test_multiline(self):
        template = "Line 1: {{ a }}\nLine 2: {{ b }}"
        result = render_prompt(template, {"a": "hello", "b": "world"})
        assert result == "Line 1: hello\nLine 2: world"


class TestLoadTestFiles:
    def _write_yaml(self, content: str) -> Path:
        f = tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False)
        f.write(content)
        f.close()
        return Path(f.name)

    def test_basic_load(self):
        path = self._write_yaml("""
prompt: "Say hello to {{ name }}"
model: claude-sonnet-4-20250514
tests:
  - name: greet
    vars:
      name: Alice
    assert:
      - type: contains
        value: "hello"
""")
        suites = load_test_files([path])
        assert len(suites) == 1
        assert suites[0]["model"] == "claude-sonnet-4-20250514"
        assert len(suites[0]["tests"]) == 1
        assert suites[0]["tests"][0]["name"] == "greet"

    def test_default_model(self):
        path = self._write_yaml("""
prompt: "Hello"
tests:
  - name: test1
    assert:
      - type: min_length
        value: 1
""")
        suites = load_test_files([path])
        assert suites[0]["model"] == "claude-sonnet-4-20250514"

    def test_missing_prompt_raises(self):
        path = self._write_yaml("""
tests:
  - name: test1
    assert:
      - type: contains
        value: "hi"
""")
        with pytest.raises(ValueError, match="Missing required 'prompt'"):
            load_test_files([path])

    def test_missing_tests_raises(self):
        path = self._write_yaml("""
prompt: "Hello"
""")
        with pytest.raises(ValueError, match="Missing required 'tests'"):
            load_test_files([path])

    def test_no_assertions_raises(self):
        path = self._write_yaml("""
prompt: "Hello"
tests:
  - name: empty_test
    assert: []
""")
        with pytest.raises(ValueError, match="has no assertions"):
            load_test_files([path])

    def test_multiple_tests(self):
        path = self._write_yaml("""
prompt: "{{ q }}"
tests:
  - name: test1
    vars:
      q: "What is 1+1?"
    assert:
      - type: contains
        value: "2"
  - name: test2
    vars:
      q: "What is 2+2?"
    assert:
      - type: contains
        value: "4"
""")
        suites = load_test_files([path])
        assert len(suites[0]["tests"]) == 2

    def test_system_prompt(self):
        path = self._write_yaml("""
prompt: "Hello"
system: "You are a pirate"
tests:
  - name: test1
    assert:
      - type: min_length
        value: 1
""")
        suites = load_test_files([path])
        assert suites[0]["system"] == "You are a pirate"
