#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

DATA_FILE = Path(__file__).resolve().parent / ".zilos_data.json"


def load_activities() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_activities(items: List[Dict[str, Any]]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


def normalize_date(value: str) -> str:
    try:
        return datetime.fromisoformat(value).date().isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD")


def format_duration(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    remainder = minutes % 60
    return f"{hours}h" + (f" {remainder}m" if remainder else "")


def add_activity(args: argparse.Namespace) -> None:
    activities = load_activities()
    activity_id = max((item["id"] for item in activities), default=0) + 1
    activity = {
        "id": activity_id,
        "name": args.name.strip(),
        "category": args.category.strip() if args.category else "general",
        "user": args.user.strip() if args.user else "anonymous",
        "duration": args.duration,
        "notes": args.notes.strip() if args.notes else "",
        "date": args.date or datetime.now().date().isoformat(),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    activities.append(activity)
    save_activities(activities)
    print(f"Added activity #{activity_id}: {activity['name']} ({activity['user']})")


def list_activities(args: argparse.Namespace) -> None:
    activities = load_activities()
    if args.today:
        today = datetime.now().date().isoformat()
        activities = [item for item in activities if item["date"] == today]
    if args.status:
        activities = [item for item in activities if item["status"] == args.status]
    if args.category:
        activities = [item for item in activities if item["category"] == args.category]
    if not activities:
        print("No activities found.")
        return

    rows = []
    for item in sorted(activities, key=lambda x: (x["date"], x["id"])):
        rows.append(
            f"#{item['id']} [{item['status']}] {item['date']} - {item['name']} ({item['category']}, user={item['user']}, {format_duration(item['duration'])})"
        )
        if item["notes"]:
            rows.append(f"    Notes: {item['notes']}")
    print("\n".join(rows))


def update_activity_status(args: argparse.Namespace, status: str) -> None:
    activities = load_activities()
    for item in activities:
        if item["id"] == args.id:
            item["status"] = status
            item["updated_at"] = datetime.now().isoformat()
            save_activities(activities)
            print(f"Activity #{args.id} marked as {status}.")
            return
    print(f"No activity found with id {args.id}.")


def remove_activity(args: argparse.Namespace) -> None:
    activities = load_activities()
    updated = [item for item in activities if item["id"] != args.id]
    if len(updated) == len(activities):
        print(f"No activity found with id {args.id}.")
        return
    save_activities(updated)
    print(f"Removed activity #{args.id}.")


def summary(args: argparse.Namespace) -> None:
    activities = load_activities()
    if args.today:
        today = datetime.now().date().isoformat()
        activities = [item for item in activities if item["date"] == today]
    if not activities:
        print("No activities to summarize.")
        return

    totals = {"pending": 0, "complete": 0, "all": 0}
    by_category = {}
    for item in activities:
        totals["all"] += item["duration"]
        totals[item["status"]] += item["duration"]
        by_category[item["category"]] = by_category.get(item["category"], 0) + item["duration"]

    print("Activity summary")
    print("--------------")
    print(f"Total time: {format_duration(totals['all'])}")
    print(f"Completed: {format_duration(totals['complete'])}")
    print(f"Pending: {format_duration(totals['pending'])}")
    print("\nTime by category:")
    for category, minutes in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {format_duration(minutes)}")


def average(args: argparse.Namespace) -> None:
    activities = load_activities()
    if args.today:
        today = datetime.now().date().isoformat()
        activities = [item for item in activities if item["date"] == today]
    if args.category:
        activities = [item for item in activities if item["category"] == args.category]
    if args.user:
        activities = [item for item in activities if item["user"] == args.user]

    if not activities:
        print("No matching activities to average.")
        return

    per_user: Dict[str, List[int]] = {}
    for item in activities:
        per_user.setdefault(item["user"], []).append(item["duration"])

    print("Average activity duration")
    print("-------------------------")
    if args.category:
        print(f"Category: {args.category}")
    if args.today:
        print(f"Date: {today}")
    if args.user:
        print(f"User: {args.user}")

    total_duration = 0
    total_count = 0
    for user, durations in sorted(per_user.items()):
        user_total = sum(durations)
        user_count = len(durations)
        total_duration += user_total
        total_count += user_count
        print(f"{user}: {format_duration(round(user_total / user_count))} average over {user_count} activity(ies)")

    if len(per_user) > 1:
        print(f"Overall average: {format_duration(round(total_duration / total_count))} over {total_count} activities")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Zilos CLI: track short daily tasks with speed and focus."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new micro activity")
    add_parser.add_argument("name", help="Activity name")
    add_parser.add_argument("-d", "--duration", type=int, default=10, help="Duration in minutes")
    add_parser.add_argument("-c", "--category", help="Category name")
    add_parser.add_argument("-u", "--user", help="User who performed the activity")
    add_parser.add_argument("-n", "--notes", help="Optional notes")
    add_parser.add_argument("--date", type=normalize_date, help="Date for the activity (YYYY-MM-DD)")
    add_parser.set_defaults(func=add_activity)

    list_parser = subparsers.add_parser("list", help="List saved activities")
    list_parser.add_argument("--today", action="store_true", help="Only show today’s activities")
    list_parser.add_argument("--status", choices=["pending", "complete"], help="Filter by status")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.set_defaults(func=list_activities)

    complete_parser = subparsers.add_parser("complete", help="Mark an activity complete")
    complete_parser.add_argument("id", type=int, help="Activity ID")
    complete_parser.set_defaults(func=lambda args: update_activity_status(args, "complete"))

    pending_parser = subparsers.add_parser("pending", help="Mark an activity pending")
    pending_parser.add_argument("id", type=int, help="Activity ID")
    pending_parser.set_defaults(func=lambda args: update_activity_status(args, "pending"))

    remove_parser = subparsers.add_parser("remove", help="Remove an activity")
    remove_parser.add_argument("id", type=int, help="Activity ID")
    remove_parser.set_defaults(func=remove_activity)

    summary_parser = subparsers.add_parser("summary", help="Show time summary")
    summary_parser.add_argument("--today", action="store_true", help="Summarize only today’s activities")
    summary_parser.set_defaults(func=summary)

    average_parser = subparsers.add_parser("average", help="Show average duration per user")
    average_parser.add_argument("--category", help="Category to average, e.g. work")
    average_parser.add_argument("--user", help="Only show averages for this user")
    average_parser.add_argument("--today", action="store_true", help="Only include today’s activities")
    average_parser.set_defaults(func=average)

    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    arguments.func(arguments)


if __name__ == "__main__":
    main()
