import os
import json
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

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable/secret not found.")
        exit(1)

    commit_sha = os.environ.get("COMMIT_SHA", "unknown")
    short_sha = commit_sha[:7]

    # Pull git diff between current HEAD and previous commit
    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD~1", "HEAD"], 
            text=True, 
            stderr=subprocess.DEVNULL
        )[:8000]
    except Exception:
        diff = ""

    # Pull latest commit message
    try:
        msg = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%B"], 
            text=True
        ).strip()
    except Exception:
        msg = "Initial Commit"

    # Identify primary modified file
    try:
        touched_files = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"], 
            text=True
        ).splitlines()
        primary_file = touched_files[0] if touched_files else "src/consensus"
    except Exception:
        primary_file = "src/consensus"

    if not diff.strip():
        print("No functional diff to process. Exiting.")
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
    res = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=40.0
    )
    res.raise_for_status()

    raw_card = json.loads(res.json()["choices"][0]["message"]["content"])
    
    # Inject repository deep-links
    raw_card["commit_hash"] = short_sha
    raw_card["repo_url"] = "https://github.com/afrodojo/hive-alignment"
    raw_card["live_site_url"] = "https://hive-align.eds-360.com"
    raw_card["external_reference"] = primary_file

    out_path = f"data/cards/{short_sha}.json"
    with open(out_path, "w") as f:
        json.dump(raw_card, f, indent=2)

    print(f"Successfully generated: {out_path}")

if __name__ == "__main__":
    main()
