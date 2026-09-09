# unslop

Cut AI tells from any writing and add human voice. Must always apply.

## When it applies

Use whenever text will be seen by a human: explanations, docs, PRs, chat
replies, prose. If it reads like a machine wrote it, scan for the patterns and
rewrite.

## What it does

1. Scans for the tell patterns listed in `SKILL.md` (content, language,
   style, communication artifacts, filler, jargon, plain speech).
2. Rewrites. Preserves meaning and matches the intended tone.
3. Adds soul: opinions, varied rhythm, first person where it fits, specifics.
4. Self-audits: asks what still makes the text obviously AI-generated and
   fixes the remaining tells.

See `SKILL.md` for the full pattern list.
