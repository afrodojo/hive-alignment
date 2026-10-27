import os
import re
from typing import List, Optional
from pydantic import BaseModel, Field
import httpx
from fastapi import APIRouter, Header, HTTPException, Request

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

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

    # In production, persist directly to PostgreSQL / Base44 DB:
    # db.execute("INSERT INTO cards ... VALUES ...")
    
    return {
        "status": "success",
        "action": "Card synthesized",
        "repo": "afrodojo/hive-alignment",
        "card": card_data
    }
