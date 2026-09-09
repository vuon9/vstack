### Babysit & Review

**You own the merge frontier. Keep status green, triage reviews, stop at the human's call.**

Use when monitoring a PR, driving CI checks to green, or addressing automated/human review comments.

1. **Check status before acting.**
   Poll the current status of the PR via `gh pr view` or `gh pr checks`.
   Distinguish between real code failures, infrastructure flakes, and merge conflicts.
2. **Never churn code blindly.**
   When automated reviewers (linters, bots, security checkers) leave comments, consult `references/triage.md`.
   Classify each comment:
   - `fix`: Clear correctness, security, performance, or behavior defect. Fix it cleanly.
   - `dismiss`: The suggestion is a false positive or intentional design choice. Dismiss with concrete proof on the thread.
   - `ask`: High-risk, ambiguous, or architecture-altering comment. Ask the user.
3. **One push wave.**
   Batch all conflict resolutions, review fixes, and CI remedies into one coherent push rather than triggering repeated CI restarts.
4. **Stop at the human line.**
   Once CI is green and review comments are triaged, stop and report.
   Do not merge unless explicitly instructed by the user.
