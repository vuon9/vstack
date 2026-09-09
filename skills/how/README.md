# how

Explain how something in the codebase works: subsystem architecture, runtime
flow, feature paths, placement and ownership questions. Enough to build a
working mental model, not annotated source code.

## Use it with a prompt

- "How does the rate limiter work?" -> subsystem explanation
- "How is the auth service structured?" -> architectural overview
- "Walk me through what happens when a user submits a form" -> runtime trace
- "What are the architectural issues here?" -> critique mode

Simple questions are answered in a single pass. Complex ones fan out parallel
explorers over distinct slices of the subsystem, then a synthesis step writes
the human-facing explanation. Critique mode explains first, then has
independent models find architectural issues and gives a lead judgment on
each.

## Relationship

Companion to `why`. `how` answers what the code does and how it works; `why`
answers what forces led to its shape. Use why for motivation.

See `SKILL.md` for the full flow and `references/` for the agent prompts.
