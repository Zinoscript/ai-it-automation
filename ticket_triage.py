"""Claude suggests a category and a reply. A HUMAN approves before anything is saved.

This is the important pattern for customer work:
the AI proposes, the human decides. Nothing is ever sent automatically.
Approved replies are only saved to approved_replies.json on your own computer.

Examples:
    python3 ticket_triage.py --dry-run
    python3 ticket_triage.py                (needs ANTHROPIC_API_KEY)
"""

import argparse
import json

from claude_client import ask_claude, parse_json_reply, should_dry_run

SYSTEM = (
    "You are an IT support assistant. Read the ticket and answer ONLY with JSON in this form: "
    '{"category": "network|account|hardware|software|other", '
    '"suggested_reply": "a short, polite first reply to the customer"}'
)

FAKE_REPLY = (
    '{"category": "other", '
    '"suggested_reply": "Hello! Thanks for contacting us. We are looking into this and will get back to you soon."}'
)

OUTPUT_FILE = "approved_replies.json"


def ask_human(question: str) -> bool:
    try:
        answer = input(question).strip().lower()
    except EOFError:
        return False
    return answer in ("y", "yes")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ticket triage with human approval")
    parser.add_argument("--file", default="tickets.json", help="ticket file (default tickets.json)")
    parser.add_argument("--dry-run", action="store_true", help="do not call the API")
    args = parser.parse_args()

    dry_run = should_dry_run(args.dry_run)

    with open(args.file, encoding="utf-8") as file:
        tickets = json.load(file)

    approved = []

    for ticket in tickets:
        if ticket["status"] == "closed":
            continue

        print(f"Ticket #{ticket['id']} ({ticket['customer']}): {ticket['title']}")
        user_message = f"Customer: {ticket['customer']}\nTitle: {ticket['title']}"
        reply = ask_claude(SYSTEM, user_message, dry_run, FAKE_REPLY)
        result = parse_json_reply(reply)

        print(f"\n  Suggested category: {result.get('category', '-')}")
        print(f"  Suggested reply:    {result.get('suggested_reply', result)}\n")

        if ask_human("  Approve this reply? [y/n] "):
            approved.append({"ticket_id": ticket["id"], **result})
            print("  Approved and saved.\n")
        else:
            print("  Skipped.\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(approved, file, indent=2, ensure_ascii=False)

    print(f"Done. {len(approved)} approved replies saved to {OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
