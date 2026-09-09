# automate-me

A guided flow for capturing an engineer's working conventions, preferences, and discipline into a personal `-mode` skill that coding agents follow.

## What it does

Instead of writing a custom system prompt or skill from scratch, `/automate-me`:
1. **Mines your recent agent history**: inspects session transcripts (Pi, OpenCode, Cursor) and git commit patterns for how you actually work (corrections, autonomy line, reply format, verification posture).
2. **Clarifies intent**: asks a few structured multiple-choice questions to confirm rules and catch missing preferences.
3. **Drafts your mode skill**: generates a personal `<handle>-mode` skill formatted with triggers, principles, and execution guidelines.
4. **Hardens the prose**: runs the draft through `unslop` to remove fluff, long dashes, and AI mannerisms.

## When to use

- "Automate me" or "turn my style into a skill".
- Creating a new personal mode (e.g. `alex-mode`, `sarah-mode`).
- Updating an existing mode skill with recent habits.
- When you find yourself repeating the same instructions ("don't add comments", "run tests first", "keep replies terse") across agent sessions.

## Output

The result is a self-contained, model-agnostic `-mode` skill installed in your global agent store (`~/.agents/skills/<handle>-mode/`) or in your repository.
