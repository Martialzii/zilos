# Zilos

Zilos is a small, installable CLI tool for tracking micro activities, focusing on work time and average duration by user.

## GitHub

- Repository: https://github.com/Martialzii/zilos
- Release: `v0.2.0`

## Features

- Add short activities with duration, category, user, and notes
- List activities by date, status, or category
- Mark activities complete or pending
- Remove activities
- Show activity summaries and average duration per user

## Install

```bash
cd c:\Users\Cyrus\firebase-project\dataconnect
python -m pip install -e .
```

## Usage

Run the CLI using the installed command or directly with Python:

```bash
zilos add "Review backlog" -d 20 -c work -u cyrus
zilos list --today
zilos average --category work
```

## Versioned script usage

```bash
python zilos_0_2_0.py add "Write notes" -d 15 -c work -u cyrus
```

## Direct script usage

```bash
python zilos.py add "Write notes" -d 15 -c work -u cyrus
```

## Notes

The data is stored locally in `.zilos_data.json` in this repository directory.
