# Code Review Plugin

Code review and quality — adversarial review and security patterns for PatternFly applications. Works in both **Claude Code** and **Cursor**.

## Installation

### Claude Code

```bash
# Add the PatternFly marketplace
/plugin marketplace add patternfly/ai-helpers

# Install the plugin
/plugin install code-review@ai-helpers
```

### Cursor

See the [root README](../../README.md) for Cursor installation options.

## File Structure

```text
code-review/
├── .claude-plugin/
│   └── plugin.json
├── .cursor-plugin/
│   └── plugin.json
├── skills/
└── README.md
```

## Sources

- [PatternFly.org](https://www.patternfly.org/)

## License

MIT
