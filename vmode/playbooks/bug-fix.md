### Bug fix

**You own the diagnosis and fix. Reproduce, isolate, verify.**

Use when resolving a defect or unintended behavior.

1. **Reproduce before touching code.**
   Reproduce the failure directly on the relevant surface.
   Create an observable repro: a failing test, a minimal runner script, or a runtime trace.
   If impossible to reproduce directly, state the concrete reason before proceeding.
   A bug you cannot reproduce is a bug you cannot prove fixed.
2. **Binary-search the cause.**
   Form candidate hypotheses. Rule them out with runtime evidence until the single mechanism survives.
   Trace the flow via the `how` pattern: follow the call chain and state transitions from trigger to failure point to isolate exactly where behavior diverged.
   Add temporary instrumentation if necessary to inspect real state. Do not guess.
3. **Plan the minimal long-term fix.**
   Check `why` before modifying existing logic: consult `git blame`, recent commits, or PR discussions to understand the intent and edge cases that shaped the current code. Do not break historical intent.
   Choose the smallest change that completely fixes the root cause. Avoid defensive band-aids that merely mask symptoms.
4. **Implement red-to-green.**
   Write the failing test or assertion first via `test-driven-development`.
   Apply the fix.
   Verify the failing reproduction now passes cleanly on the exact same surface.
5. **Local review.**
   Review the diff via `hunk-review`. Confirm no leftover temporary debug instrumentation remains. If no live Hunk review session is active, run `requesting-code-review` on the local diff or dispatch a fresh reviewer subagent with the diff to audit the changes.
