import os
import re
from typing import List, Optional
from pydantic import BaseModel, Field
import httpx
from fastapi import APIRouter, Header, HTTPException, Request

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

BASE44_APP_ID = os.getenv("BASE44_APP_ID")
# Personal access token (Workspace settings > Secrets > Personal access tokens)
BASE44_PAT = os.getenv("BASE44_PAT")
BASE44_API_BASE = "https://app.base44.com/api/apps"
GITHUB_REPO_URL = "https://github.com/afrodojo/hive-alignment"
LIVE_SITE_URL = "https://hive-align.eds-360.com"

# Pydantic schema enforcing the exact Base44 database card structure
class CardExtractionSchema(BaseModel):
    domain: str = Field(
        default="CS_RESEARCH",
        description="Must be CS_RESEARCH unless the commit strictly touches governance, ethics, or business."
    )
    title: str = Field(max_length=120, description="Punchy, technical title (e.g., 'TLA+ State Guard Invariants')")
    hook: str = Field(max_length=255, description="One-sentence hook framing the problem or breakthrough.")
    core_insight: str = Field(description="High-density paragraph explaining the architectural mechanism or proof.")
    takeaways: List[str] = Field(min_length=2, max_length=3, description="2-3 actionable, high-leverage takeaways.")
    proof_or_code: Optional[str] = Field(description="Relevant code snippet, AST logic, or formal LaTeX math expression.")
    read_time_seconds: int = Field(default=45)

SYSTEM_PROMPT = """
You are an executive research compiler for an AI Solutions Architect, Cyber SME, and CS Doctoral researcher working on autonomic multi-agent zero-trust swarms.

Your input is a raw Git commit diff or push event from the repository 'afrodojo/hive-alignment'.
Extract the key architectural, mathematical, security, or algorithmic updates and compress them into a 45-second micro-learning card.

Guidelines:
1. Discard trivial formatting, typos, or dependency bumps.
2. If the commit contains mathematical logic, state transition safety checks, or distributed invariants, output the formal invariant in LaTeX for 'proof_or_code'.
3. Maintain an uncompromising, high-density technical tone.
4. Output must strictly conform to the JSON schema.
"""

async def synthesize_card_from_diff(diff_text: str, commit_msg: str) -> dict:
    """Invokes LLM structured outputs to generate the card payload."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    user_content = f"Commit Message:\n{commit_msg}\n\nGit Diff:\n{diff_text[:12000]}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
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
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        import json
        return json.loads(content)

def extract_touched_files(diff_text: str) -> List[str]:
    """Pull post-image paths out of a unified diff, preserving order."""
    paths: List[str] = []
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:].strip()
            if path and path != "dev/null" and path not in paths:
                paths.append(path)
    return paths


async def persist_card_to_base44(card_data: dict, commit_hash: str, touched_files: List[str]) -> dict:
    """Inserts the synthesized card into Base44 via the public Data API."""
    if not BASE44_APP_ID or not BASE44_PAT:
        raise RuntimeError("BASE44_APP_ID and BASE44_PAT must be set.")

    payload = {
        "domain": card_data.get("domain", "CS_RESEARCH"),
        "title": card_data.get("title"),
        "hook": card_data.get("hook"),
        "core_insight": card_data.get("core_insight"),
        "takeaways": card_data.get("takeaways", []),
        "proof_or_code": card_data.get("proof_or_code"),
        "read_time_seconds": card_data.get("read_time_seconds", 45),
        "commit_hash": (commit_hash or "")[:7],
        "repo_url": GITHUB_REPO_URL,
        "live_site_url": LIVE_SITE_URL,
        "external_reference": touched_files[0] if touched_files else None,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            f"{BASE44_API_BASE}/{BASE44_APP_ID}/entities/Card",
            headers={
                "Authorization": f"Bearer {BASE44_PAT}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        res.raise_for_status()
        return res.json()


@router.post("/github-commit")
async def handle_github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None)
):
    """
    Receives push and PR events from https://github.com/afrodojo/hive-alignment.
    """
    if x_github_event not in ["push", "pull_request"]:
        return {"status": "ignored", "reason": f"Event '{x_github_event}' not processed."}

    payload = await request.json()

    # Extract commit metadata and diffs
    commits = payload.get("commits", [])
    if not commits and "pull_request" in payload:
        commits = [{
            "message": payload["pull_request"].get("title", "") + "\n" + payload["pull_request"].get("body", ""),
            "url": payload["pull_request"].get("diff_url", "")
        }]

    if not commits:
        return {"status": "noop", "message": "No commits found in payload."}

    latest_commit = commits[-1]
    commit_msg = latest_commit.get("message", "No message provided")
    
    # Fetch unified diff via GitHub API or the diff URL
    diff_text = ""
    compare_url = payload.get("compare")
    if compare_url:
        async with httpx.AsyncClient() as client:
            # Append .diff to get raw diff
            diff_res = await client.get(f"{compare_url}.diff", headers={"Accept": "application/vnd.github.v3.diff"})
            if diff_res.status_code == 200:
                diff_text = diff_res.text

    if not diff_text:
        diff_text = commit_msg

    # Generate synthesized card
    card_data = await synthesize_card_from_diff(diff_text, commit_msg)

    commit_hash = latest_commit.get("id") or payload.get("after") or ""
    touched_files = extract_touched_files(diff_text)

    try:
        persisted = await persist_card_to_base44(card_data, commit_hash, touched_files)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Base44 rejected the card: {exc.response.text}",
        )

    return {
        "status": "success",
        "action": "Card synthesized and persisted",
        "repo": "afrodojo/hive-alignment",
        "commit": commit_hash[:7],
        "card": persisted
    }