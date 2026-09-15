# use-siyuan

Drive the SiYuan note-taking app from its `siyuan` CLI: browse notebooks and
documents, read and write blocks, run full-text or SQL queries, and export,
import, snapshot, or sync a workspace. The CLI embeds the kernel, so it works
directly on workspace files without the desktop app running.

## Use it with a prompt

- "What's in my SiYuan Work notebook?" -> notebook + document discovery
- "Show the outline of my Onboarding doc" -> `outline get`
- "Append this to my daily note" -> `dailynote append`
- "Search my notes for EAZE-119" -> `search` / `ref backlinks`
- "Export that document to Markdown" -> `export md`

## Before anything else

Data commands default to `$HOME/SiYuan` and fail with `directory not found` if
that path is not a workspace. Resolve the real path with `siyuan workspace
list` and pass it with `-w <path>` on every command. Passing `-w` also
registers that path permanently, so avoid pointing it at throwaway copies
unless you want them listed.

## Relationship

Reference skill for the SiYuan CLI surface. `SKILL.md` holds the mental model,
the canonical workflows, and the gotchas worth knowing up front;
`references/commands.md` is the full command catalog with signatures. Pair it
with `how` or `why` when the question is about SiYuan internals rather than
driving the CLI.

See `SKILL.md` for the workflow and `references/commands.md` for every group
and subcommand.