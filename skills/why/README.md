# why

Investigate the motivation and intent behind code: why it was built this way,
which edge cases shaped it, what product, business, or operational constraints
applied, and what alternatives were rejected.

## Use it with a prompt

- "Why was X designed this way?" -> design rationale
- "Why do we do X instead of Y?" -> tradeoffs and alternatives
- "What edge cases motivated this?" -> defensive reasoning
- "Why does this code still exist?" -> dead-code territory
- "What's the history of X?" -> archaeological sweep

Historical context spreads across seven evidence categories (source control,
issue tracking, long-form docs, real-time chat, observability, error tracking,
product analytics). The skill enumerates available MCPs at run time, queries
all categories in parallel, and returns a cited read with calibrated
confidence. Null results are first-class evidence.

## Relationship

Companion to `how`. `how` answers what the code does and how it works; `why`
answers what forces led to its shape. Use how for runtime behavior.

See `SKILL.md` for the operating posture and `references/epistemics.md` for the
confidence framework.
