Assess a PatternFly bug report for level of effort, design involvement, alternative solutions, and similar past issues.

## Input

The user provides one of:
- A GitHub issue URL (e.g. `https://github.com/patternfly/patternfly-react/issues/1234`)
- A repo name and issue number (e.g. `patternfly-react #1234`)
- Just an issue number if the repo is obvious from context

Parse the owner and repo from the input. The owner is always `patternfly`. Supported repos include `patternfly-react`, `patternfly`, `patternfly-org`, `patternfly-design`, and any other repo under the `patternfly` GitHub org.

## Workflow

### Step 1: Read the bug

Use the GitHub MCP `issue_read` tool with `method: "get"` to fetch the issue details. Then use `method: "get_comments"` to read the discussion. Also use `method: "get_labels"` to get assigned labels.

Extract from the issue:
- **Title and description** — what is broken
- **Component(s) affected** — which PatternFly component(s) are involved
- **Reproduction steps** — how to trigger the bug
- **Labels** — priority, component area, breaking change indicators

### Step 2: Look up affected components

For each PatternFly component mentioned in the bug, use the PatternFly MCP `searchPatternFlyDocs` tool to find its documentation. Then use `usePatternFlyDocs` to read the component's API, usage guidelines, and design guidelines.

This gives you the context to understand:
- How the component is intended to work
- What props/behaviors are relevant to the bug
- Whether design guidelines constrain the fix

### Step 3: Search for similar issues

Use the GitHub MCP `search_issues` tool to find related bugs. Run multiple searches:

1. **Same component, same repo:** `repo:patternfly/{repo} label:{component-label} {key terms from title}`
2. **Same symptoms across repos:** `org:patternfly {error message or behavior description}`
3. **Closed similar issues:** `repo:patternfly/{repo} is:closed {key terms}`

For each similar issue found, check whether it was fixed, closed as duplicate, closed as won't-fix, or is still open. Read comments on the most relevant matches (up to 3) to understand conclusions.

### Step 4: Assess effort

Use this rubric to estimate story points:

| Points | Criteria |
|--------|----------|
| **1** | Typo, wrong prop value, missing CSS class, copy-paste fix. One file, no behavior change. |
| **2** | Small logic fix, prop addition, minor styling. 1-2 files, straightforward testing. |
| **3** | Moderate fix touching component logic. May need new tests, 2-4 files affected. |
| **5** | Significant change: new prop, refactored behavior, cross-component interaction. Needs thorough test coverage and review. |
| **8** | Complex fix across multiple components or packages. May require API changes, deprecation, or migration path. |
| **13** | Architectural change, major refactor, or new component/pattern. Needs RFC or design review. |

Consider these factors:
- **Scope** — how many files, components, and packages are affected
- **Risk** — could the fix break existing consumers
- **Testing** — what new or updated tests are needed
- **Dependencies** — does the fix depend on upstream changes

### Step 5: Evaluate design team involvement

Flag that design input is needed when any of these apply:

- The bug involves visual appearance, spacing, or layout
- The fix would change how the component looks or behaves from the user's perspective
- The component's design guidelines are ambiguous about the expected behavior
- The bug reporter suggests a UI change as the fix
- The issue involves responsive behavior, states (hover, focus, disabled), or animations
- The fix would deviate from PatternFly design guidelines
- Multiple valid visual solutions exist and the "right" answer is a design decision

If none apply, state that the fix is implementation-only and does not need design review.

### Step 6: Identify alternative solutions

For each bug, consider at least two approaches:
- **Direct fix** — the most obvious code change to resolve the reported behavior
- **Workaround** — a consumer-side workaround the reporter could use today
- **Alternative approach** — a different technical strategy (e.g. prop vs CSS vs component restructure)

For each alternative, briefly note the trade-off: risk, effort, backwards compatibility.

## Output

Produce a conversational assessment with recommendations. Cover these areas naturally — don't force rigid headings if the context doesn't warrant it:

**Effort estimate** — Story points with a brief justification referencing scope, risk, and complexity.

**Design team involvement** — Whether design input is needed and why, or a clear statement that it's implementation-only.

**Alternative solutions** — The approaches you identified with trade-offs. Lead with the recommended approach.

**Similar issues** — Past issues that relate, what happened with them, and whether any conclusions apply. If no similar issues exist, say so.

End with a one-sentence recommendation: what to do next (e.g. "Assign to a developer as a 3-point story" or "Bring to design review before starting implementation").

## Tips

- If the bug report is vague or missing reproduction steps, flag that in your assessment and note that effort may change once details are clarified.
- When the component is deprecated or has a replacement planned, mention that context.
- If a similar issue was already fixed, check whether the fix regressed or the reporter might be on an older version.
- For bugs involving accessibility, note that WCAG conformance is non-negotiable and alternatives should all satisfy a11y requirements.
