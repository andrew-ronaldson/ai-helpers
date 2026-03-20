Assess a PatternFly issue report for level of effort, design involvement, alternative solutions, and similar past issues.

## Input

The user provides one of:
- A GitHub issue URL (e.g. `https://github.com/patternfly/patternfly-react/issues/1234`)
- A repo name and issue number (e.g. `patternfly-react #1234`)
- Just an issue number if the repo is obvious from context

Parse the owner and repo from the input. The owner is always `patternfly`. Supported repos include `patternfly-react`, `patternfly`, `patternfly-org`, `patternfly-design`, and any other repo under the `patternfly` GitHub org.

## Workflow

### Step 1: Read the issue

Use the GitHub MCP `issue_read` tool with `method: "get"` to fetch the issue details. Then use `method: "get_comments"` to read the discussion. Also use `method: "get_labels"` to get assigned labels.

Extract from the issue:
- **Title and description** — what is broken
- **Component(s) affected** — which PatternFly component(s) are involved
- **Reproduction steps** — how to trigger the issue
- **Labels** — priority, component area, breaking change indicators

### Step 2: Look up affected components

For each PatternFly component mentioned in the issue, use the PatternFly MCP `searchPatternFlyDocs` tool to find its documentation. Then use `usePatternFlyDocs` to read the component's API, usage guidelines, and design guidelines.

This gives you the context to understand:
- How the component is intended to work
- What props/behaviors are relevant to the issue
- Whether design guidelines constrain the fix

### Step 3: Search for similar issues

Use the GitHub MCP `search_issues` tool to find related issues. Always search across these three core repos, plus the source repo if it differs:

- `patternfly/patternfly-react` — React component issues and behavior issues
- `patternfly/patternfly` — Core HTML/CSS issues, layout issues, design token problems
- `patternfly/patternfly-design` — Design change requests, UX issues, feature proposals

Run these searches (adjust key terms from the issue title and description):

1. **Same component in patternfly-react:** `repo:patternfly/patternfly-react {component name} {key symptoms}`
2. **CSS/layout side in patternfly core:** `repo:patternfly/patternfly {component name} {key symptoms}`
3. **Design discussions:** `repo:patternfly/patternfly-design {component name} {key symptoms}`
4. **Broad org search for the same symptoms:** `org:patternfly {error message or behavior description}`
5. **Closed matches in the source repo:** `repo:patternfly/{source-repo} is:closed {key terms}`

A issue in `patternfly-react` may have a root cause tracked in `patternfly` (CSS/HTML) or a design decision recorded in `patternfly-design`. Cross-repo matches are especially valuable — flag them prominently.

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

- The issue involves visual appearance, spacing, or layout
- The fix would change how the component looks or behaves from the user's perspective
- The component's design guidelines are ambiguous about the expected behavior
- The issue reporter suggests a UI change as the fix
- The issue involves responsive behavior, states (hover, focus, disabled), or animations
- The fix would deviate from PatternFly design guidelines
- Multiple valid visual solutions exist and the "right" answer is a design decision

If none apply, state that the fix is implementation-only and does not need design review.

### Step 6: Identify alternative solutions

For each issue, consider at least two approaches:
- **Direct fix** — the most obvious code change to resolve the reported behavior
- **Workaround** — a consumer-side workaround the reporter could use today
- **Alternative approach** — a different technical strategy (e.g. prop vs CSS vs component restructure)

For each alternative, briefly note the trade-off: risk, effort, backwards compatibility.

### Step 7: Check for cross-repo follow-up issues

When the source issue is in `patternfly/patternfly` (core HTML/CSS), evaluate whether the fix will require a corresponding change in `patternfly/patternfly-react`. Per the PatternFly core contributing guidelines, a follow-up issue must be created in `patternfly-react` when:

- The CSS/HTML change affects a React component's rendering or behavior
- Global CSS variables or design tokens are modified
- Animation or transition changes need React-side coordination
- A new CSS modifier class requires a new prop or prop value in the React wrapper

If a follow-up is needed, prompt the user:

> **React follow-up needed:** This core CSS change affects the `{ComponentName}` React component. A follow-up issue should be filed in [patternfly/patternfly-react](https://github.com/patternfly/patternfly-react/issues/new) that includes:
> - Reference to this core issue (patternfly/patternfly#{number})
> - The core release version that will contain the fix
> - A description of what changed and how it affects the React component
>
> Would you like me to draft the follow-up issue?

If the user confirms, use the GitHub MCP `issue_write` tool to create the issue in `patternfly/patternfly-react` with the details above.

Similarly, if the source issue is in `patternfly-react` but the root cause appears to be in core CSS/HTML, note that a fix may need to land in `patternfly/patternfly` first and flag the dependency.

## Output

Produce a conversational assessment with recommendations. Cover these areas naturally — don't force rigid headings if the context doesn't warrant it:

**Effort estimate** — Story points with a brief justification referencing scope, risk, and complexity.

**Design team involvement** — Whether design input is needed and why, or a clear statement that it's implementation-only.

**Alternative solutions** — The approaches you identified with trade-offs. Lead with the recommended approach.

**Similar issues** — Past issues that relate, what happened with them, and whether any conclusions apply. If no similar issues exist, say so.

End with a one-sentence recommendation: what to do next (e.g. "Assign to a developer as a 3-point story" or "Bring to design review before starting implementation").

## Tips

- If the issue report is vague or missing reproduction steps, flag that in your assessment and note that effort may change once details are clarified.
- When the component is deprecated or has a replacement planned, mention that context.
- If a similar issue was already fixed, check whether the fix regressed or the reporter might be on an older version.
- For issues involving accessibility, note that WCAG conformance is non-negotiable and alternatives should all satisfy a11y requirements.
