# AMC Quiz

A terminal quiz app for studying for the Australian Medical Council (AMC) exam.
It generates multiple-choice questions from Murtagh's General Practice textbook
and uses spaced repetition to help you focus on what you got wrong.

## First-time setup (Windows)

### 1. Install uv (a Python package manager)

Open **PowerShell** and run:

```
winget install astral-sh.uv
```

Close and reopen PowerShell after installing so the `uv` command is available.

### 2. Download the code

```
git clone https://github.com/nick/amc-quiz.git
cd amc-quiz
```

### 3. Install dependencies

```
uv sync
```

This creates a virtual environment and installs everything the app needs.
You only need to do this once (or again if dependencies change).

### 4. Set up your OpenAI API key

Create a file called `.env` in the `amc-quiz` folder with this line:

```
OPENAI_API_KEY=sk-...your-key-here...
```

Ask Nick for the key if you don't have one.

## Running the app

From the `amc-quiz` folder, run:

```
uv run amc-quiz
```

A terminal interface will open. Use arrow keys to navigate and Enter to select.

## What you can do in the app

- **Study** — pick a chapter or type a topic to get 5 multiple-choice questions
- **Review** — re-do questions you got wrong, spaced out over time so you remember them
- **Progress** — see how you're doing across all topics
- **Q&A** — ask any question and get an answer from the textbook
