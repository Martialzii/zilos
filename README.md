# Zilos

Zilos is a small, installable CLI tool for tracking micro activities, focusing on work time, projects, and advanced reporting.

## GitHub

- Repository: https://github.com/Martialzii/zilos
- Release: `v0.3.0`

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
zilos add "Review backlog" -d 20 -c work -p zilos-app -u cyrus --priority high
zilos list --today --project zilos-app
zilos average --category work
zilos stats --today --project zilos-app
zilos export --path zilos_report.csv --project zilos-app
```

## Versioned script usage

```bash
python zilos_0_3_0.py add "Write notes" -d 15 -c work -p zilos-app -u cyrus --priority medium
```

## Previous version access

The prior released version is still available as an alias script:

```bash
python zilos_0_2_0.py add "Write notes" -d 15 -c work -u cyrus
```

Use this when you need the older `v0.2.0` behavior while keeping the new `v0.3.0` workflow active.

## Direct script usage

```bash
python zilos.py add "Write notes" -d 15 -c work -p zilos-app -u cyrus --priority medium
```

## Notes

The data is stored locally in `.zilos_data.json` in this repository directory.
