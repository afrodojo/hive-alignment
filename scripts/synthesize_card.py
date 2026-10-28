import os
import json
import time
import subprocess
import httpx
from pydantic import BaseModel, Field

class CardExtractionSchema(BaseModel):
    domain: str = Field(default="CS_RESEARCH")
    title: str = Field(max_length=120)
    hook: str = Field(max_length=255)
    core_insight: str
    takeaways: list[str] = Field(min_length=2, max_length=3)
    proof_or_code: str = Field(description="Strict LaTeX expression or concise AST code block")
    read_time_seconds: int = 45

# Paths that should NEVER trigger AI card synthesis
IGNORED_PREFIXES = (
    ".github/",
    "data/telemetry/",
    "data/cards/",
    "README.md",
    "LICENSE",
    ".gitignore"
)

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[WARN] OPENAI_API_KEY secret not found. Skipping synthesis cleanly.")
        return

    commit_sha = os.environ.get("COMMIT_SHA", "unknown")
    short_sha = commit_sha[:7]

    # Pull list of touched files
    try:
        touched_files = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"], 
            text=True
        ).splitlines()
    except Exception:
        touched_files = []

    # Check if commit contains relevant domain files
    substantive_files = [
        f for f in touched_files 
        if not any(f.startswith(prefix) for prefix in IGNORED_PREFIXES)
    ]

    if not substantive_files and touched_files:
        print(f"[SKIP] Commit {short_sha} only touched ignored files ({touched_files}). Exiting cleanly.")
        return

    primary_file = substantive_files[0] if substantive_files else "src/consensus"

    # Pull git diff between HEAD~1 and HEAD
    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD~1", "HEAD", "--", *substantive_files] if substantive_files else ["git", "diff", "HEAD~1", "HEAD"], 
            text=True, 
            stderr=subprocess.DEVNULL
        )[:8000]
    except Exception:
        diff = ""

    # Pull commit message
    try:
        msg = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%B"], 
            text=True
        ).strip()
    except Exception:
        msg = "Initial Commit"

    if not diff.strip():
        print(f"[SKIP] No functional diff to process for commit {short_sha}. Exiting.")
        return

    system_prompt = (
        "You are an executive research compiler for an AI Solutions Architect and CS Doctoral researcher.\n"
        "Convert the raw Git commit diff into a high-density, 45-second micro-learning card.\n"
        "Strict rules:\n"
        "1. Extract architectural invariants, Byzantine consensus bounds, zero-trust attestation, or algorithmic updates.\n"
        "2. Formulate mathematical or system checks as LaTeX in 'proof_or_code'.\n"
        "3. Output strictly according to the CardExtractionSchema."
    )

    user_content = f"Commit: {msg}\nPrimary File: {primary_file}\n\nDiff:\n{diff}"

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "CardExtractionSchema",
                "schema": CardExtractionSchema.model_json_schema()
            }
        }
    }

    print(f"Synthesizing card for commit {short_sha}...")

    # Retry loop with backoff for rate limits and quota handling
    max_retries = 3
    base_delay = 3
    raw_card = None

    for attempt in range(max_retries):
        try:
            res = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                timeout=45.0
            )

            if res.status_code == 429:
                err_data = res.json().get("error", {})
                err_message = err_data.get("message", "Rate limit / Quota exceeded")
                print(f"[WARN] OpenAI 429 Encountered: {err_message} (Attempt {attempt + 1}/{max_retries})")

                # If quota is exhausted or credit is $0, backoff won't help; exit cleanly without breaking CI
                if "quota" in err_message.lower() or "billing" in err_message.lower():
                    print("[ABORT] OpenAI account quota exhausted or billing inactive. Skipping card generation without failing build.")
                    return

                time.sleep(base_delay * (2 ** attempt))
                continue

            res.raise_for_status()
            raw_card = json.loads(res.json()["choices"][0]["message"]["content"])
            break

        except httpx.HTTPStatusError as e:
            print(f"[ERROR] HTTP error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                print("[SKIP] Max retries reached. Exiting cleanly.")
                return
            time.sleep(base_delay * (2 ** attempt))
        except Exception as e:
            print(f"[ERROR] Unexpected error during synthesis: {e}")
            return

    if not raw_card:
        print("[SKIP] Failed to obtain card schema from OpenAI. Exiting.")
        return

    # Inject repository deep-links
    raw_card["commit_hash"] = short_sha
    raw_card["repo_url"] = "https://github.com/afrodojo/hive-alignment"
    raw_card["live_site_url"] = "https://hive-align.eds-360.com"
    raw_card["external_reference"] = primary_file

    os.makedirs("data/cards", exist_ok=True)
    out_path = f"data/cards/{short_sha}.json"
    with open(out_path, "w") as f:
        json.dump(raw_card, f, indent=2)

    print(f"Successfully generated: {out_path}")

if __name__ == "__main__":
    main()
