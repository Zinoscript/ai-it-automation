"""Ask Claude to summarize each open support ticket and suggest a priority.

Only use fake or anonymized tickets (customer-A, customer-B, ...).
Do not send real customer data to any AI tool unless your company has approved it.

Examples:
    python3 ticket_summarizer.py --dry-run
    python3 ticket_summarizer.py            (needs ANTHROPIC_API_KEY)
"""

import argparse
import json

from claude_client import ask_claude, parse_json_reply, should_dry_run

SYSTEM = (
    "You are an IT support assistant. Read the ticket and answer ONLY with JSON "
    'in this form: {"summary": "one short sentence", "priority": "low|medium|high"}'
)

FAKE_REPLY = '{"summary": "Example summary (dry run).", "priority": "medium"}'


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize support tickets with Claude")
    parser.add_argument("--file", default="tickets.json", help="ticket file (default tickets.json)")
    parser.add_argument("--dry-run", action="store_true", help="do not call the API")
    args = parser.parse_args()

    dry_run = should_dry_run(args.dry_run)

    with open(args.file, encoding="utf-8") as file:
        tickets = json.load(file)

    open_tickets = [t for t in tickets if t["status"] != "closed"]
    print(f"Found {len(open_tickets)} open tickets.\n")

    for ticket in open_tickets:
        print(f"Ticket #{ticket['id']} ({ticket['customer']}): {ticket['title']}")
        user_message = f"Customer: {ticket['customer']}\nTitle: {ticket['title']}"
        reply = ask_claude(SYSTEM, user_message, dry_run, FAKE_REPLY)
        result = parse_json_reply(reply)
        print(f"  Summary:  {result.get('summary', result)}")
        print(f"  Priority: {result.get('priority', '-')} (yours was: {ticket['priority']})\n")


if __name__ == "__main__":
    main()
