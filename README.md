# promptlab ⚡

Automated testing for LLM prompts. Write test cases in YAML, run them against Claude or OpenAI, get pass/fail results in your terminal.

**Like pytest, but for prompts.**

```bash
pip install promptlab-cli
promptlab run tests/
```

```
✅ summarize_article :: returns_short_summary        PASS (1.2s)
✅ summarize_article :: mentions_key_points           PASS (1.1s)
❌ translate_text :: preserves_tone                   FAIL (0.9s)
   Expected: contains "formal"
   Got: "Here is the translated text in a casual style..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Results: 2 passed, 1 failed, 3 total (3.2s)
```

## Why?

You're building an app with Claude or GPT. Your prompt works today. Tomorrow you tweak it and something breaks. You don't notice until a user complains.

**promptlab catches prompt regressions before they ship.** Define what good output looks like, run tests on every change, and know immediately if something broke.

## Quickstart

### Install

```bash
pip install promptlab-cli
```

### Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or
export OPENAI_API_KEY=sk-...
```

### Write a test file

Create `tests/summarize.yaml`:

```yaml
prompt: |
  Summarize this article in 2-3 sentences:
  {{ article }}

model: claude-sonnet-4-20250514

tests:
  - name: short_summary
    vars:
      article: |
        The Federal Reserve held interest rates steady on Wednesday,
        keeping the benchmark rate in the 5.25%-5.50% range. Chair
        Jerome Powell said the committee needs more confidence that
        inflation is moving toward the 2% target before cutting rates.
    assert:
      - type: max_tokens
        value: 100
      - type: contains
        value: "Federal Reserve"
      - type: contains
        value: "interest rate"

  - name: handles_empty_input
    vars:
      article: ""
    assert:
      - type: not_contains
        value: "error"
      - type: min_length
        value: 10
```

### Run it

```bash
promptlab run tests/
```

## Test File Format

Each `.yaml` file defines a prompt and its test cases:

```yaml
# The prompt template. Use {{ variable }} for inputs.
prompt: |
  You are a helpful assistant. {{ instruction }}

# Which model to use
model: claude-sonnet-4-20250514   # or gpt-4o, claude-haiku-4-5-20251001, etc.

# Optional system prompt
system: "You are a concise technical writer."

# Optional model parameters
temperature: 0
max_tokens: 500

# Test cases
tests:
  - name: test_name
    vars:
      instruction: "Explain what a CPU does in one sentence."
    assert:
      - type: contains
        value: "processor"
      - type: max_tokens
        value: 50
```

## Assertion Types

| Type | Description | Example |
|---|---|---|
| `contains` | Output must contain this string (case-insensitive) | `value: "machine learning"` |
| `not_contains` | Output must NOT contain this string | `value: "I'm sorry"` |
| `starts_with` | Output must start with this string | `value: "Sure"` |
| `regex` | Output must match this regex pattern | `value: "\\d{4}"` |
| `max_tokens` | Output must be at most N tokens | `value: 100` |
| `min_length` | Output must be at least N characters | `value: 50` |
| `max_length` | Output must be at most N characters | `value: 500` |
| `equals` | Output must exactly equal this string | `value: "42"` |
| `llm_judge` | Ask another LLM to evaluate the output | `value: "Is this response helpful and accurate?"` |

## LLM-as-Judge

The most powerful assertion type. Uses a second LLM call to evaluate output quality:

```yaml
tests:
  - name: helpful_response
    vars:
      question: "How do I fix a memory leak in Python?"
    assert:
      - type: llm_judge
        value: "Does this response provide specific, actionable debugging steps? Answer YES or NO."
```

## Supported Models

**Anthropic (Claude):**
- `claude-sonnet-4-20250514`
- `claude-haiku-4-5-20251001`
- Set `ANTHROPIC_API_KEY` environment variable

**OpenAI:**
- `gpt-4o`
- `gpt-4o-mini`
- Set `OPENAI_API_KEY` environment variable

## CLI Commands

```bash
# Run all test files in a directory
promptlab run tests/

# Run a single test file
promptlab run tests/summarize.yaml

# Verbose output (show full LLM responses)
promptlab run tests/ --verbose

# Output results as JSON
promptlab run tests/ --json

# Dry run (show what would be tested without calling APIs)
promptlab run tests/ --dry-run
```

## Use Cases

- **Prompt regression testing** — Run tests in CI/CD to catch regressions
- **Prompt comparison** — Test the same cases across different models
- **Guard rails validation** — Verify your prompt rejects harmful inputs
- **Output format checking** — Ensure structured output matches expectations

## Development

```bash
git clone https://github.com/vigp17/promptlab.git
cd promptlab
pip install -e ".[dev]"
pytest
```

## Roadmap

- [x] YAML test definitions
- [x] Claude and OpenAI support
- [x] 9 assertion types including LLM-as-judge
- [x] CLI with colored output
- [ ] Cost tracking per test run
- [ ] HTML report generation
- [ ] Parallel test execution
- [ ] GitHub Actions integration
- [ ] Prompt versioning and diff
- [ ] Custom scoring functions

## License

MIT
