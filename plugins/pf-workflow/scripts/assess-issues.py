"""
Daily PatternFly issue triage.

Queries new issues across patternfly repos, assesses each one for effort,
design involvement, alternatives, and similar past issues, then posts the
assessment as an issue comment.

Required environment variables:
  GITHUB_TOKEN        - GitHub PAT with repo/issues write access to patternfly org
  ANTHROPIC_API_KEY   - Anthropic API key for Claude
  HOURS_LOOKBACK      - How many hours back to search (default: 24)
  DRY_RUN             - If "true", print assessments without posting comments
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import anthropic
import requests

REPOS = [
    ("patternfly", "patternfly-react"),
    ("patternfly", "patternfly"),
    ("patternfly", "patternfly-design"),
]

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HOURS_LOOKBACK = int(os.environ.get("HOURS_LOOKBACK", "24"))
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

SKILL_PATH = Path(__file__).parent.parent / "skills" / "bug-assessment" / "SKILL.md"

TRIAGE_COMMENT_MARKER = "<!-- pf-workflow-triage-bot -->"


def gh(method, path, **kwargs):
    """Make a GitHub API request."""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"{GITHUB_API}{path}" if path.startswith("/") else path
    resp = getattr(requests, method)(url, headers=headers, **kwargs)
    resp.raise_for_status()
    return resp.json() if resp.text else {}


def get_new_issues(owner, repo, since):
    """Fetch issues created since the given datetime."""
    issues = gh("get", f"/repos/{owner}/{repo}/issues", params={
        "state": "open",
        "sort": "created",
        "direction": "desc",
        "since": since.isoformat(),
        "per_page": 50,
    })
    return [i for i in issues if "pull_request" not in i and i["created_at"] >= since.isoformat()]


def get_issue_comments(owner, repo, issue_number):
    """Fetch comments on an issue."""
    return gh("get", f"/repos/{owner}/{repo}/issues/{issue_number}/comments", params={"per_page": 30})


def already_triaged(comments):
    """Check if we already posted a triage comment."""
    return any(TRIAGE_COMMENT_MARKER in (c.get("body") or "") for c in comments)


def search_similar(title, labels, owner, repo):
    """Search for similar issues across all three repos."""
    keywords = " ".join(title.split()[:6])
    label_names = [l["name"] for l in labels if l["name"] not in ("PF Team", "enhancement", "bug")]
    label_q = f" label:{label_names[0]}" if label_names else ""

    searches = [
        f"repo:patternfly/patternfly-react {keywords}",
        f"repo:patternfly/patternfly {keywords}",
        f"repo:patternfly/patternfly-design {keywords}",
        f"repo:patternfly/{repo} is:closed {keywords}{label_q}",
    ]

    results = []
    for query in searches:
        try:
            data = gh("get", "/search/issues", params={
                "q": f"is:issue {query}",
                "sort": "updated",
                "order": "desc",
                "per_page": 5,
            })
            for item in data.get("items", []):
                if item["number"] != 0 and not any(r["number"] == item["number"] and r["repo"] == item["repository_url"] for r in results):
                    results.append({
                        "number": item["number"],
                        "title": item["title"],
                        "state": item["state"],
                        "html_url": item["html_url"],
                        "repo": item["repository_url"],
                        "body": (item.get("body") or "")[:500],
                    })
        except requests.HTTPError:
            continue

    return results[:15]


def build_prompt(issue, comments, similar, owner, repo, skill_text):
    """Build the LLM prompt with issue context and the skill rubric."""
    similar_text = "\n".join(
        f"- [{s['title']}]({s['html_url']}) ({s['state']}): {s['body'][:200]}..."
        for s in similar
    ) or "No similar issues found."

    comments_text = "\n".join(
        f"**@{c['user']['login']}:** {(c.get('body') or '')[:500]}"
        for c in comments[:5]
    ) or "No comments yet."

    labels_text = ", ".join(l["name"] for l in issue.get("labels", [])) or "None"

    return f"""You are a PatternFly project triager. Assess the following GitHub issue using the
rubric and workflow below. Produce a concise assessment suitable for posting as an issue comment.

## Skill Instructions

{skill_text}

## Issue to Assess

**Repository:** {owner}/{repo}
**Issue:** #{issue['number']} — {issue['title']}
**Type:** {issue.get('type', {}).get('name', 'Unknown') if isinstance(issue.get('type'), dict) else 'Unknown'}
**Labels:** {labels_text}
**Created:** {issue['created_at']}
**Author:** @{issue['user']['login']}

**Description:**
{(issue.get('body') or 'No description provided.')[:3000]}

## Comments

{comments_text}

## Similar Issues Found

{similar_text}

## Instructions

Follow the skill workflow to produce the assessment. Skip steps 1-3 (data gathering) since the
data is provided above. Execute steps 4-7 (assess effort, evaluate design involvement, identify
alternatives, check for cross-repo follow-ups).

Format the output as a GitHub issue comment with markdown. Keep it concise but thorough.
Start with a brief summary line, then cover effort, design involvement, alternatives, and
similar issues. End with a recommendation.

Do NOT include the hidden marker comment — that will be added automatically."""


def assess_issue(issue, comments, similar, owner, repo, skill_text):
    """Call Claude to produce the assessment."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = build_prompt(issue, comments, similar, owner, repo, skill_text)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def post_comment(owner, repo, issue_number, body):
    """Post an assessment comment on the issue."""
    full_body = f"{TRIAGE_COMMENT_MARKER}\n\n## Automated Triage Assessment\n\n{body}"
    gh("post", f"/repos/{owner}/{repo}/issues/{issue_number}/comments", json={"body": full_body})


def main():
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is required", file=sys.stderr)
        sys.exit(1)
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY is required", file=sys.stderr)
        sys.exit(1)

    skill_text = SKILL_PATH.read_text() if SKILL_PATH.exists() else ""
    if not skill_text:
        print(f"Warning: Skill file not found at {SKILL_PATH}", file=sys.stderr)

    since = datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)
    print(f"Looking for issues created since {since.isoformat()}")
    print(f"Dry run: {DRY_RUN}\n")

    total_assessed = 0

    for owner, repo in REPOS:
        print(f"\n{'='*60}")
        print(f"Checking {owner}/{repo}...")

        try:
            issues = get_new_issues(owner, repo, since)
        except requests.HTTPError as e:
            print(f"  Error fetching issues: {e}")
            continue

        print(f"  Found {len(issues)} new issue(s)")

        for issue in issues:
            issue_num = issue["number"]
            print(f"\n  Assessing #{issue_num}: {issue['title']}")

            comments = get_issue_comments(owner, repo, issue_num)
            if already_triaged(comments):
                print(f"    Skipping — already triaged")
                continue

            similar = search_similar(issue["title"], issue.get("labels", []), owner, repo)
            print(f"    Found {len(similar)} similar issue(s)")

            try:
                assessment = assess_issue(issue, comments, similar, owner, repo, skill_text)
            except Exception as e:
                print(f"    Error generating assessment: {e}")
                continue

            if DRY_RUN:
                print(f"\n    --- Assessment (dry run) ---")
                print(f"    {assessment[:500]}...")
            else:
                try:
                    post_comment(owner, repo, issue_num, assessment)
                    print(f"    Posted assessment comment")
                except requests.HTTPError as e:
                    print(f"    Error posting comment: {e}")
                    continue

            total_assessed += 1

    print(f"\n{'='*60}")
    print(f"Done. Assessed {total_assessed} issue(s).")


if __name__ == "__main__":
    main()
