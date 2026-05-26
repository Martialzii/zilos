#!/usr/bin/env python3
import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_FILE = Path(__file__).resolve().parent / ".zilos_data.json"
CONFIG_FILE = Path(__file__).resolve().parent / ".zilos_config.json"


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


def load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_config(config: Dict[str, Any]) -> None:
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def normalize_date(value: str) -> str:
    try:
        return datetime.fromisoformat(value).date().isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD")


def normalize_tags(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [tag.strip() for tag in value.split(",") if tag.strip()]


def format_duration(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    remainder = minutes % 60
    return f"{hours}h" + (f" {remainder}m" if remainder else "")


def filter_activities(activities: List[Dict[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    if args.today:
        today = datetime.now().date().isoformat()
        activities = [item for item in activities if item["date"] == today]
    if getattr(args, "status", None):
        activities = [item for item in activities if item["status"] == args.status]
    if getattr(args, "category", None):
        activities = [item for item in activities if item["category"] == args.category]
    if getattr(args, "user", None):
        activities = [item for item in activities if item["user"] == args.user]
    if getattr(args, "project", None):
        activities = [item for item in activities if item["project"] == args.project]
    if getattr(args, "priority", None):
        activities = [item for item in activities if item["priority"] == args.priority]
    if getattr(args, "tags", None):
        requested_tag = args.tags.strip()
        activities = [item for item in activities if requested_tag in item.get("tags", [])]
    return activities


def add_activity(args: argparse.Namespace) -> None:
    activities = load_activities()
    activity_id = max((item["id"] for item in activities), default=0) + 1
    activity = {
        "id": activity_id,
        "name": args.name.strip(),
        "category": args.category.strip() if args.category else "general",
        "project": args.project.strip() if args.project else "default",
        "user": args.user.strip() if args.user else "anonymous",
        "priority": args.priority,
        "tags": normalize_tags(args.tags),
        "recurring": args.recurring,
        "duration": args.duration,
        "notes": args.notes.strip() if args.notes else "",
        "date": args.date or datetime.now().date().isoformat(),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    activities.append(activity)
    save_activities(activities)
    print(f"Added activity #{activity_id}: {activity['name']} ({activity['user']}, project={activity['project']})")


def list_activities(args: argparse.Namespace) -> None:
    activities = filter_activities(load_activities(), args)
    if not activities:
        print("No activities found.")
        return

    rows = []
    for item in sorted(activities, key=lambda x: (x["date"], x["id"])):
        rows.append(
            f"#{item['id']} [{item['status']}] {item['date']} - {item['name']} ({item['project']}, {item['category']}, user={item['user']}, priority={item['priority']}, recurring={item['recurring']}, tags={','.join(item['tags']) if item['tags'] else 'none'}, {format_duration(item['duration'])})"
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
    activities = filter_activities(load_activities(), args)
    if not activities:
        print("No activities to summarize.")
        return

    totals = {"pending": 0, "complete": 0, "all": 0}
    by_category = {}
    by_project = {}
    for item in activities:
        totals["all"] += item["duration"]
        totals[item["status"]] += item["duration"]
        by_category[item["category"]] = by_category.get(item["category"], 0) + item["duration"]
        by_project[item["project"]] = by_project.get(item["project"], 0) + item["duration"]

    print("Activity summary")
    print("--------------")
    print(f"Total time: {format_duration(totals['all'])}")
    print(f"Completed: {format_duration(totals['complete'])}")
    print(f"Pending: {format_duration(totals['pending'])}")
    print("\nTime by project:")
    for project, minutes in sorted(by_project.items(), key=lambda x: x[1], reverse=True):
        print(f"  {project}: {format_duration(minutes)}")
    print("\nTime by category:")
    for category, minutes in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {format_duration(minutes)}")


def average(args: argparse.Namespace) -> None:
    activities = filter_activities(load_activities(), args)
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
    if args.project:
        print(f"Project: {args.project}")
    if args.today:
        today = datetime.now().date().isoformat()
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


def stats(args: argparse.Namespace) -> None:
    activities = filter_activities(load_activities(), args)
    if not activities:
        print("No activities found for stats.")
        return

    totals = {"all": 0, "complete": 0, "pending": 0}
    by_project = {}
    by_user = {}
    by_priority = {}
    by_category = {}

    for item in activities:
        totals["all"] += item["duration"]
        totals[item["status"]] += item["duration"]
        by_project[item["project"]] = by_project.get(item["project"], 0) + item["duration"]
        by_user[item["user"]] = by_user.get(item["user"], 0) + item["duration"]
        by_priority[item["priority"]] = by_priority.get(item["priority"], 0) + item["duration"]
        by_category[item["category"]] = by_category.get(item["category"], 0) + item["duration"]

    print("Zilos activity stats")
    print("-------------------")
    print(f"Total activities: {len(activities)}")
    print(f"Total time: {format_duration(totals['all'])}")
    print(f"Completed time: {format_duration(totals['complete'])}")
    print(f"Pending time: {format_duration(totals['pending'])}")

    def print_breakdown(title: str, data: Dict[str, int]) -> None:
        print(f"\n{title}:")
        for key, minutes in sorted(data.items(), key=lambda x: x[1], reverse=True):
            print(f"  {key}: {format_duration(minutes)}")

    print_breakdown("Time by project", by_project)
    print_breakdown("Time by user", by_user)
    print_breakdown("Time by priority", by_priority)
    print_breakdown("Time by category", by_category)


def export_activities(args: argparse.Namespace) -> None:
    activities = filter_activities(load_activities(), args)
    if not activities:
        print("No activities available to export.")
        return

    path = Path(args.path).resolve()
    if args.format == "json":
        with path.open("w", encoding="utf-8") as f:
            json.dump(activities, f, indent=2, ensure_ascii=False)
    else:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "id",
                    "name",
                    "project",
                    "category",
                    "priority",
                    "tags",
                    "recurring",
                    "user",
                    "duration",
                    "status",
                    "date",
                    "notes",
                    "created_at",
                ],
            )
            writer.writeheader()
            for item in activities:
                writer.writerow(
                    {
                        "id": item.get("id", ""),
                        "name": item.get("name", ""),
                        "project": item.get("project", ""),
                        "category": item.get("category", ""),
                        "priority": item.get("priority", ""),
                        "tags": ",".join(item.get("tags", [])),
                        "recurring": item.get("recurring", "none"),
                        "user": item.get("user", ""),
                        "duration": item.get("duration", ""),
                        "status": item.get("status", ""),
                        "date": item.get("date", ""),
                        "notes": item.get("notes", ""),
                        "created_at": item.get("created_at", ""),
                    }
                )

    print(f"Exported {len(activities)} activities to {path}")


def due_activities(args: argparse.Namespace) -> None:
    activities = filter_activities(load_activities(), args)
    if args.overdue:
        today = datetime.now().date().isoformat()
        activities = [item for item in activities if item["date"] < today and item["status"] != "complete"]
    if not activities:
        print("No due activities found.")
        return

    print("Due activities")
    print("--------------")
    for item in sorted(activities, key=lambda x: (x["date"], x["id"])):
        print(
            f"#{item['id']} {item['date']} - {item['name']} ({item['project']}, {item['category']}, user={item['user']}, priority={item['priority']}, recurring={item['recurring']})"
        )


def setup_paypal(args: argparse.Namespace) -> None:
    config = load_config()
    config["paypal_email"] = args.paypal_email.strip()
    save_config(config)
    print(f"Saved PayPal merchant email: {config['paypal_email']}")


def subscription(args: argparse.Namespace) -> None:
    config = load_config()
    paypal_email = config.get("paypal_email")
    if not paypal_email:
        print("No PayPal email configured. Use `zilos setup-paypal --paypal-email you@example.com`.")
        return
    print("PayPal subscription stub")
    print(f"Merchant: {paypal_email}")
    print("Open this stub URL on your browser to simulate a subscription setup:")
    print("https://www.paypal.com/checkoutnow?merchant=YOUR_MERCHANT_ID")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Zilos CLI: track short daily tasks with speed and focus."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new micro activity")
    add_parser.add_argument("name", help="Activity name")
    add_parser.add_argument("-d", "--duration", type=int, default=10, help="Duration in minutes")
    add_parser.add_argument("-c", "--category", help="Category name")
    add_parser.add_argument("-p", "--project", help="Project name")
    add_parser.add_argument("-u", "--user", help="User who performed the activity")
    add_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        default="medium",
        help="Task priority",
    )
    add_parser.add_argument("--tags", help="Comma-separated tags to attach to the activity")
    add_parser.add_argument(
        "--recurring",
        choices=["none", "daily", "weekly", "monthly"],
        default="none",
        help="Recurring interval for the activity",
    )
    add_parser.add_argument("-n", "--notes", help="Optional notes")
    add_parser.add_argument("--date", type=normalize_date, help="Date for the activity (YYYY-MM-DD)")
    add_parser.set_defaults(func=add_activity)

    list_parser = subparsers.add_parser("list", help="List saved activities")
    list_parser.add_argument("--today", action="store_true", help="Only show today’s activities")
    list_parser.add_argument("--status", choices=["pending", "complete"], help="Filter by status")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--user", help="Filter by user")
    list_parser.add_argument("--project", help="Filter by project")
    list_parser.add_argument("--priority", choices=["low", "medium", "high"], help="Filter by priority")
    list_parser.add_argument("--tags", help="Filter by tag")
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
    summary_parser.add_argument("--project", help="Summarize only this project")
    summary_parser.add_argument("--category", help="Summarize only this category")
    summary_parser.set_defaults(func=summary)

    average_parser = subparsers.add_parser("average", help="Show average duration per user")
    average_parser.add_argument("--category", help="Category to average, e.g. work")
    average_parser.add_argument("--project", help="Project to average")
    average_parser.add_argument("--user", help="Only show averages for this user")
    average_parser.add_argument("--today", action="store_true", help="Only include today’s activities")
    average_parser.set_defaults(func=average)

    stats_parser = subparsers.add_parser("stats", help="Show richer breakdowns by project/user/priority")
    stats_parser.add_argument("--today", action="store_true", help="Only include today’s activities")
    stats_parser.add_argument("--category", help="Filter by category")
    stats_parser.add_argument("--project", help="Filter by project")
    stats_parser.add_argument("--user", help="Filter by user")
    stats_parser.add_argument("--priority", choices=["low", "medium", "high"], help="Filter by priority")
    stats_parser.set_defaults(func=stats)

    export_parser = subparsers.add_parser("export", help="Export filtered activities to CSV or JSON")
    export_parser.add_argument("--path", default="zilos_export.csv", help="Export file path")
    export_parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Export format")
    export_parser.add_argument("--today", action="store_true", help="Only export today’s activities")
    export_parser.add_argument("--category", help="Filter by category")
    export_parser.add_argument("--project", help="Filter by project")
    export_parser.add_argument("--user", help="Filter by user")
    export_parser.add_argument("--priority", choices=["low", "medium", "high"], help="Filter by priority")
    export_parser.add_argument("--tags", help="Filter by tag")
    export_parser.set_defaults(func=export_activities)

    due_parser = subparsers.add_parser("due", help="List due or overdue activities")
    due_parser.add_argument("--overdue", action="store_true", help="Show only overdue activities")
    due_parser.add_argument("--project", help="Filter by project")
    due_parser.add_argument("--category", help="Filter by category")
    due_parser.add_argument("--user", help="Filter by user")
    due_parser.add_argument("--priority", choices=["low", "medium", "high"], help="Filter by priority")
    due_parser.set_defaults(func=due_activities)

    paypal_setup = subparsers.add_parser("setup-paypal", help="Save your PayPal merchant email")
    paypal_setup.add_argument("--paypal-email", required=True, help="PayPal merchant email")
    paypal_setup.set_defaults(func=setup_paypal)

    subscription_parser = subparsers.add_parser("subscription", help="Show PayPal subscription stub info")
    subscription_parser.set_defaults(func=subscription)

    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    arguments.func(arguments)


if __name__ == "__main__":
    main()
