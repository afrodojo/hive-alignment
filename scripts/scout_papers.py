import os
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import requests

SUPA_URL = os.environ.get("SUPABASE_URL", "https://jsyooxahstzrhipbocss.supabase.co").rstrip("/")
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "")
TARGET_EMAIL = os.environ.get("HIVE_USER_EMAIL", "cyberdojosensei@gmail.com").strip().lower()
SCOUT_QUERY = os.environ.get(
    "DOCTORAL_SCOUT_QUERY",
    "heart rate variability cognitive self-regulation executive function",
).strip()


def supa_headers(extra=None):
    h = {
        "apikey": SUPA_KEY,
        "Authorization": f"Bearer {SUPA_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h


def distill_paper(title: str, abstract: str):
    clean = re.sub(r"\s+", " ", (abstract or "")).strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean) if 30 <= len(s.strip()) <= 260]
    thesis = sentences[0] if sentences else clean[:180] or f"Empirical study on {title}."
    method = sentences[1] if len(sentences) > 1 else f"Review methodology and sample design in {title}."
    finding = sentences[2] if len(sentences) > 2 else f"Synthesize primary outcome metrics from {title}."

    return {
        "takeaway": thesis,
        "microSteps": [
            f"1. Core Thesis: {thesis}",
            f"2. Method & Mechanism: {method}",
            f"3. Active Recall & Gap Check: {finding}",
        ],
        "quiz": [
            {
                "q": f"1. What is the primary empirical thesis investigated in \"{title}\"?",
                "a": thesis,
            },
            {
                "q": f"2. What methodological approach or key finding is reported in \"{title}\"?",
                "a": method,
            },
            {
                "q": f"3. Applied Synthesis: How does \"{title}\" inform your January 2027 Literature Matrix?",
                "a": finding,
            },
        ],
    }


def scout_arxiv(query: str, max_results: int = 2):
    papers = []
    try:
        url = (
            "http://export.arxiv.org/api/query?"
            f"search_query=all:{requests.utils.quote(query)}&start=0&max_results={max_results}"
            "&sortBy=submittedDate&sortOrder=descending"
        )
        res = requests.get(url, timeout=20)
        if not res.ok:
            return papers
        root = ET.fromstring(res.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for idx, entry in enumerate(root.findall("atom:entry", ns)):
            title = re.sub(r"\s+", " ", (entry.findtext("atom:title", "", ns) or "")).strip()
            summary = re.sub(r"\s+", " ", (entry.findtext("atom:summary", "", ns) or "")).strip()
            published = (entry.findtext("atom:published", "", ns) or "")[:10]
            authors = [
                a.findtext("atom:name", "", ns).strip()
                for a in entry.findall("atom:author", ns)
                if a.findtext("atom:name", "", ns)
            ]
            author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
            if published:
                author_str = f"{author_str} ({published[:4]})"

            distilled = distill_paper(title, summary)
            papers.append(
                {
                    "id": f"kv_scout_arxiv_{today}_{idx}",
                    "title": title,
                    "domain": "Doctoral Studies",
                    "resourceFormat": "Academic Paper (Peer-Reviewed)",
                    "author": author_str or "arXiv Preprint",
                    "sectionRef": f"arXiv Open Access • {published}",
                    "researchGap": "Evaluate methodological transferability to doctoral dissertation design.",
                    "scoutSource": "arXiv",
                    "duration": "20-Min Deep Sprint",
                    "type": "Doctoral Studies • Weekly Paper Scout",
                    "takeaway": distilled["takeaway"],
                    "content": summary[:6000],
                    "microSteps": distilled["microSteps"],
                    "quiz": distilled["quiz"],
                    "masteryLevel": 0,
                    "nextReviewDate": today,
                    "quizScore": None,
                    "date": today,
                }
            )
    except Exception as exc:
        print(f"arXiv scout warning: {exc}")
    return papers


def scout_europe_pmc(query: str, max_results: int = 2):
    papers = []
    try:
        full_q = f"({query}) AND OPEN_ACCESS:y"
        url = (
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
            f"query={requests.utils.quote(full_q)}&resultType=core&format=json&pageSize={max_results}"
        )
        res = requests.get(url, timeout=20)
        if not res.ok:
            return papers
        results = (res.json().get("resultList") or {}).get("result") or []
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for idx, r in enumerate(results):
            title = (r.get("title") or "").rstrip(".").strip()
            abstract = (r.get("abstractText") or "").strip()
            if not title or len(abstract) < 60:
                continue
            author_str = (r.get("authorString") or "PubMed Central Author").rstrip(".")
            pub_year = str(r.get("pubYear") or datetime.now(timezone.utc).year)
            journal = r.get("journalTitle") or "PubMed Central"
            pmcid = r.get("pmcid") or ""

            distilled = distill_paper(title, abstract)
            papers.append(
                {
                    "id": f"kv_scout_pmc_{today}_{idx}",
                    "title": title,
                    "domain": "Doctoral Studies",
                    "resourceFormat": "Academic Paper (Peer-Reviewed)",
                    "author": f"{author_str} ({pub_year})",
                    "sectionRef": f"{journal} {pmcid}".strip(),
                    "researchGap": "Synthesize empirical effect sizes & measurement instruments in Matrix.",
                    "scoutSource": "Europe PMC",
                    "duration": "20-Min Deep Sprint",
                    "type": "Doctoral Studies • Weekly Paper Scout",
                    "takeaway": distilled["takeaway"],
                    "content": abstract[:6000],
                    "microSteps": distilled["microSteps"],
                    "quiz": distilled["quiz"],
                    "masteryLevel": 0,
                    "nextReviewDate": today,
                    "quizScore": None,
                    "date": today,
                }
            )
    except Exception as exc:
        print(f"Europe PMC scout warning: {exc}")
    return papers


def main():
    if not SUPA_KEY:
        print("ERROR: Missing SUPABASE_SERVICE_ROLE_KEY environment variable.")
        return

    scouted = scout_arxiv(SCOUT_QUERY, 2) + scout_europe_pmc(SCOUT_QUERY, 2)
    print(f"Scouted {len(scouted)} open-access papers for query: '{SCOUT_QUERY}'")
    if not scouted:
        return

    url = f"{SUPA_URL}/rest/v1/brotherhood_status?brother=eq.{requests.utils.quote(TARGET_EMAIL)}&select=*"
    res = requests.get(url, headers=supa_headers(), timeout=20)
    if not (res.ok and res.json()):
        print("No existing row found in brotherhood_status; run wearable sync or sign in first.")
        return

    row = res.json()[0]
    state_data = row.get("data") or {}
    if not isinstance(state_data, dict):
        state_data = {}

    existing_scouted = state_data.get("scoutedPapers") or []
    seen_titles = {p.get("title", "").lower() for p in existing_scouted}
    for p in scouted:
        if p["title"].lower() not in seen_titles:
            existing_scouted.insert(0, p)
            seen_titles.add(p["title"].lower())

    state_data["scoutedPapers"] = existing_scouted[:25]
    now_iso = datetime.now(timezone.utc).isoformat()

    patch_url = f"{SUPA_URL}/rest/v1/brotherhood_status?brother=eq.{requests.utils.quote(TARGET_EMAIL)}"
    patch_res = requests.patch(
        patch_url,
        headers=supa_headers({"Prefer": "return=minimal"}),
        data=json.dumps({"data": state_data, "updated_at": now_iso}),
        timeout=20,
    )
    print("Supabase scoutedPapers PATCH status:", patch_res.status_code)


if __name__ == "__main__":
    main()
