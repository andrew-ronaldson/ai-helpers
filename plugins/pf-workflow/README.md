# PatternFly Workflow Plugin

AI plugin for PatternFly project workflow tasks including bug triage, effort estimation, and issue management. Works in both **Claude Code** and **Cursor**.

## Installation

### Claude Code

```bash
# Add the PatternFly marketplace
/plugin marketplace add patternfly/ai-helpers

# Install the plugin
/plugin install pf-workflow@ai-helpers
```

### Cursor

See the [root README](../../README.md) for Cursor installation options.

## What's Included

### Skills

Skills are tasks that produce a result.

**Bug Assessment** (`/pf-workflow:bug-assessment`) — Assess a PatternFly bug report for level of effort (story points), design team involvement, alternative solutions, and similar past issues. Works with any repo under the `patternfly` GitHub org.

### PatternFly MCP Server

Skills have access to the [PatternFly MCP server](https://github.com/patternfly/patternfly-mcp) for looking up component documentation and design guidelines.

### GitHub MCP

Skills use the GitHub MCP to read issues, search for similar bugs, and review past conclusions. Requires a GitHub MCP server to be available in your environment.

## Automated Daily Triage (GitHub Actions)

A GitHub Actions workflow runs the bug assessment skill automatically every weekday at 9:00 AM UTC. It queries new issues across `patternfly-react`, `patternfly`, and `patternfly-design`, runs each through the assessment rubric via Claude, and posts the triage as an issue comment.

### Setup

Add these secrets to your repository (Settings > Secrets and variables > Actions):

| Secret | Description |
|--------|-------------|
| `PF_TRIAGE_GITHUB_TOKEN` | GitHub PAT with `repo` and `issues:write` scope for the `patternfly` org |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |

The default `GITHUB_TOKEN` won't work because it's scoped to the `ai-helpers` repo, not the `patternfly` org repos where issues live.

### Manual trigger

You can run the workflow manually from the Actions tab with optional inputs:

- **hours_lookback** — How far back to search (default: 24 hours)
- **dry_run** — If `true`, prints assessments to the log without posting comments

### How it works

1. Queries the GitHub API for issues created in the last 24 hours
2. Skips any issue that already has a triage comment (idempotent)
3. Searches for similar issues across all three repos
4. Sends the issue context + skill rubric to Claude for assessment
5. Posts the assessment as a comment on the issue

### Customization

Edit `plugins/pf-workflow/scripts/assess-issues.py` to:

- Add or remove repos from the `REPOS` list
- Adjust the Claude model in the `assess_issue` function
- Change the comment format or add labels

## File Structure

```
pf-workflow/
├── .claude-plugin/
│   └── plugin.json        # Plugin manifest + MCP server config
├── .cursor-plugin/
│   └── plugin.json        # Identical copy for Cursor
├── skills/
│   └── bug-assessment/
│       └── SKILL.md
├── scripts/
│   └── assess-issues.py   # Daily triage script (used by GitHub Actions)
└── README.md
```

## Sources

- [PatternFly.org](https://www.patternfly.org/)
- [PatternFly React GitHub](https://github.com/patternfly/patternfly-react)
- [PatternFly MCP Server](https://github.com/patternfly/patternfly-mcp)

## License

MIT
