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
└── README.md
```

## Sources

- [PatternFly.org](https://www.patternfly.org/)
- [PatternFly React GitHub](https://github.com/patternfly/patternfly-react)
- [PatternFly MCP Server](https://github.com/patternfly/patternfly-mcp)

## License

MIT
