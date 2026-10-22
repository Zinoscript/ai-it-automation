"""Small helper that sends one question to the Claude API.

Uses only the Python standard library, so there is nothing to install.

- The API key is read from the environment variable ANTHROPIC_API_KEY.
  Never write the key in a file and never upload it to GitHub.
- In dry-run mode nothing is sent. The script shows what WOULD be sent
  and returns a made-up answer, so you can test the whole flow for free.
"""

import json
import os
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-5-5"


def get_api_key():
    return os.environ.get("ANTHROPIC_API_KEY")


def should_dry_run(dry_run_flag: bool) -> bool:
    """Dry run if the user asked for it, or if there is no API key."""
    if dry_run_flag:
        return True
    if not get_api_key():
        print("No ANTHROPIC_API_KEY found, so running in DRY-RUN mode.\n")
        return True
    return False


def ask_claude(system: str, user: str, dry_run: bool, fake_reply: str, max_tokens: int = 400) -> str:
    model = os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL)

    body = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }

    if dry_run:
        print("  [dry-run] Would send this request to the Claude API:")
        print(f"  [dry-run]   model:  {model}")
        print(f"  [dry-run]   system: {system}")
        print(f"  [dry-run]   user:   {user}")
        return fake_reply

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": get_api_key(),
            "anthropic-version": API_VERSION,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise SystemExit(f"The API returned an error: {error.code}. Check your key and model name.")
    except urllib.error.URLError as error:
        raise SystemExit(f"Could not connect to the API: {error.reason}")

    return data["content"][0]["text"]


def parse_json_reply(text: str) -> dict:
    """Claude should answer with JSON. If it does not, keep the raw text."""
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except ValueError:
        return {"raw": text}
