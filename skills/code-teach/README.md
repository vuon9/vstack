# code-teach

Teach a body of work plainly so the person actually understands it: what it
is, how it works, and why it's built that way, in one account at their pace.
The goal is understanding, not change.

## Use it with a prompt

- "Teach me this" / "help me really understand X" / "explain this change or
  subsystem to me" -> starts a teach pass

Teach decides the few things the person should walk away understanding from
why they asked and what they already know, then builds the explanation from a
plain definition upward. It keeps the discussion a conversation, shows the
mechanism rather than naming it, and draws diagrams that grow one piece at a
time.

## Relationship to other skills

Teach sits on top of `how` and `why` and blends what they find into one clear
explanation:

- `how` answers what the code does and how it works
- `why` answers what forces led to its shape
- `code-teach` runs both and weaves their findings into a single plain account

Output is written through `unslop`, in plain spoken English.

See `SKILL.md` for the full method.
