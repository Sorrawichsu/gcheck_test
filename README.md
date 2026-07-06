# gcheck

Check if a website is accessible from your location, and query a Google
genai agent, from the command line.

## Install

```bash
pip install git+https://github.com/Sorrawichsu/gcheck_test.git
```

Or via Homebrew:

```bash
brew install sorrawichsu/gcheck/gcheck
```

## Setup

`gcheck` needs a Google API key for the `ask`, `code`, `search` commands and
for generating a checklist when `check` finds a site is blocked.

```bash
cp .env.example .env
# then edit .env and set GOOGLE_API_KEY=your_key
```

## Usage

```bash
# Check if a website is reachable; get a remediation checklist if it's blocked
gcheck check example.com

# Ask the agent a question
gcheck ask "What's the capital of France?"

# Give the agent a coding task (it can write and run code)
gcheck code "write a fibonacci function in python"

# Search the web and get a summarized answer
gcheck search "latest news on rust 2024 edition"
```

## Development

```bash
pip install -e .
```

## License

MIT
