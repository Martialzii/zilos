# Zilos CLI

A small, marketable micro-activity tracker for daily focus and productivity.

## What it does

- Adds short activities like "Plan meeting", "Write outline", or "Review notes"
- Stores duration, category, user, notes, and date
- Tracks project and priority for every activity
- Supports tags and recurring schedules
- Lists all activities or just today’s work
- Marks items complete with a single command
- Summarizes total time and project breakdowns
- Calculates average activity duration by user
- Shows advanced stats by user, project, category, and priority
- Exports activity data to CSV or JSON
- Provides PayPal setup and subscription stub commands
- Keeps previous version accessible via `zilos_0_2_0.py`
- Provides versioned CLI files: `zilos_0_3_0.py`, `zilos_0_4_0.py`

## Why this is marketable

- Targets freelancers, creators, and knowledge workers
- Helps users stay accountable with micro activity goals
- Easy to demo as a fast CLI tool for daily habits
- Can be extended into a web app, browser extension, or mobile companion later

## Usage

- Add an activity:
  ```bash
  python activity_tracker.py add "Review client backlog" -d 15 -c work -n "Focus on priorities"
  ```

- List today’s activities:
  ```bash
  python activity_tracker.py list --today
  ```

- Mark complete:
  ```bash
  python activity_tracker.py complete 1
  ```

- Show summary:
  ```bash
  python activity_tracker.py summary --today
  ```

## Next growth ideas

- Add reminders or timeboxing
- Export tasks to CSV or calendar apps
- Add tags, pomodoro sessions, or streak tracking
- Build a companion web UI or mobile interface
