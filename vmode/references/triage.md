# Review & Bot Triage

Use this reference when triaging bot comments, automated code reviews, or linter warnings during PR review or babysitting. Never churn code merely to satisfy a bot comment without verifying its merit.

## Decision Rubric

Classify each finding before touching code:

- `fix`: The comment identifies a real correctness, security, data loss, race condition, or boundary bug. Fix it in the owning file, verify with a test, and cite the fix.
- `dismiss`: The comment flags a false positive, intentional design decision, or out-of-scope nit that would increase complexity for zero gain. Reply on the thread with a concise, concrete disproof and resolve.
- `ask`: The finding touches high-risk domains (auth, permissions, payments, data migrations) or involves ambiguous product tradeoffs. Ask the user before acting.

## Common Dismissal Patterns

1. **Intentional UI / styling change**: The diff intentionally altered a visual layout or component default. The bot flags the change as a deviation from previous styling.
   - *Dismiss rule*: Verify the change matches the user's intent or design spec. Provide a concise explanation.
2. **Upstream or out-of-scope invariants**: The bot flags a missing boundary check inside an internal helper where the caller already guarantees validity.
   - *Dismiss rule*: Point to the upstream guard enforcing the invariant.
3. **Temporary coexistence during migration**: A new function or module lives beside legacy code awaiting cleanup.
   - *Dismiss rule*: Confirm the dual-state is temporary and intentional.
4. **False positives on error handling**: The bot suggests catching all errors when catching a specific error type is necessary to preserve downstream behavior.
   - *Dismiss rule*: Explain why widening the error condition would mask real operational failures.

## Hard Rules

- Never commit cosmetic workarounds that complicate architecture just to silence a linter warning.
- Do not dismiss security or data-integrity warnings without concrete code proof that the vulnerability cannot manifest.
