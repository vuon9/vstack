# SiYuan CLI command catalog (v3.8.3)

Global flags: `-w, --workspace <path>`, `-f, --format table|json`,
`--dry-run`, `-v, --log-level off|trace|debug|info|warn|error|fatal`,
`-h, --help`, `--version`.

Content input flags shared by write commands: `--data <markdown>` or
`--file <path>` (`-` = stdin).

## workspace

| Command | Purpose |
| --- | --- |
| `workspace list` | List registered workspaces (name + path) |
| `workspace info` | Show active workspace path, version, validity |

## notebook

| Command | Signature |
| --- | --- |
| `notebook list` | List all notebooks (id, name, closed, sort) |
| `notebook create` | `--name <name>`; prints new notebook ID |
| `notebook rename` | `--id <id> --name <name>` |
| `notebook remove` | `--id <id>` |
| `notebook open` / `notebook close` | `--id <id>` |
| `notebook set-icon` | `--id <id> --icon <emoji hex/char/path/url>` |
| `notebook random-icon` | `[--id <id>]` (omit to update all) |

## document

| Command | Signature |
| --- | --- |
| `document list` | `--notebook <id> [--path <internal>] [--hpath <human>]` |
| `document search` | `<keyword>` (returns box, hPath, path) |
| `document get` / `document info` | `--id <docID>` |
| `document create` | `--notebook <id> --title <t> [--markdown <md>] [--path /]`; prints doc ID |
| `document rename` | `--id <id> --title <t>` |
| `document duplicate` | `--id <id>` |
| `document move` | `--id <id> --notebook <id> [--path /] [--hpath ...]` |
| `document remove` | `--id <id>` |

## block

| Command | Signature |
| --- | --- |
| `block get` | `--id <id>` block info |
| `block batch-get` | `--ids id1,id2,...` |
| `block kramdown` | `--id <id> [--mode md|textmark]` (Markdown with IAL ids) |
| `block batch-kramdown` | `--ids id1,id2,...` |
| `block children` | `--id <parentID>` |
| `block breadcrumb` | `--id <id>` ancestor path |
| `block dom` | `--id <id>` rendered DOM |
| `block stat` | `--id <id>` characters, words, blocks, links, refs |
| `block append` | `--parent <id> (--data <md> \| --file <p>)`; prints new block ID |
| `block prepend` | `--parent <id> (--data \| --file)` |
| `block insert` | `--parent <id> [--previous <siblingID>] (--data \| --file)` |
| `block update` | `--id <id> (--data \| --file) [--lock-type]` |
| `block move` | `--id <id> --parent <id> [--previous <siblingID>]` |
| `block delete` | `--id <id>` |

## attr

| Command | Signature |
| --- | --- |
| `attr get` | `--id <id>` |
| `attr batch-get` | `--ids id1,id2,...` |
| `attr set` | `--id <id> --attr name=value` (repeatable). Common: `icon`, `title-img`, `tags` |

`icon` accepts emoji hex (`1f4ca`), emoji char, custom image path, or URL.
`title-img` needs CSS: `--attr title-img='background-image:url("assets/x.jpg")'`.

## outline

| Command | Signature |
| --- | --- |
| `outline get` | `--id <docID>` heading tree with node IDs |

## ref

| Command | Signature |
| --- | --- |
| `ref backlinks` | `--id <id> [--keyword <k>] [--sort 0-7]` |
| `ref mentions` | `--id <id> [--keyword <k>] [--sort 0-7]` |
| `ref refresh` | `--id <id>` rebuild backlink index for a block |

## search

`search <query> [flags]`

| Flag | Meaning |
| --- | --- |
| `-m, --method` | 0=keyword 1=query-syntax 2=sql 3=regex 4=semantic |
| `-t, --type` | block types (document, heading, paragraph, list, codeBlock, ...) |
| `--subtype` | u (unordered), o (ordered), t (task) |
| `-g, --group-by` | 0=none 1=document |
| `-n, --notebook` | notebook ID filter (repeatable) |
| `--path` | path prefix filter (repeatable) |
| `-o, --order-by` | 0=type 1=created-asc 2=created-desc 3=updated-asc 4=updated-desc 5=content 6=relevance-asc 7=relevance-desc |
| `-p, --page`, `-s, --page-size` | pagination (default size 32) |
| `--asset` | search asset file contents instead of blocks |
| `--ext` | asset extension filter (asset mode) |
| `--get-asset` | treat query as asset path, return indexed content |

## sql

`sql <statement> [-l, --limit N]` (default 100). Main tables: `blocks`,
`assets`, `attributes`, `refs`, `spans`. Useful `blocks` columns: `id`,
`parent_id`, `root_id`, `box`, `path`, `hpath`, `name`, `alias`, `memo`,
`tag`, `content`, `markdown`, `type`, `subtype`, `sort`, `created`, `updated`.

## export

| Command | Signature |
| --- | --- |
| `export md` | `--id <id> [--output <file>]` (default stdout) |
| `export html` / `export preview` | `--id <id> [--output <file>]` |
| `export docx` | `--id <id> --output <file>` (required) |
| `export md-zip` / `export sy` | `--id <id> [--output <file>]` (default temp path) |
| `export data` | `[--output <file>]` full workspace backup |

## import

| Command | Signature |
| --- | --- |
| `import md` | `--file <p> --notebook <id> [--path /] [--hpath ...]` |
| `import sy` | `--file <p.sy.zip> --notebook <id> [--path /] [--hpath ...]` |
| `import data` | `--file <backup.zip>` |

## dailynote

| Command | Signature |
| --- | --- |
| `dailynote create` | `--notebook <id>` |
| `dailynote append` | `--notebook <id> (--data <md> \| --file <p>)` |
| `dailynote prepend` | `--notebook <id> (--data <md> \| --file <p>)` |

## database (attribute views)

| Command | Signature |
| --- | --- |
| `database search` | `<keyword>` |
| `database get` | `--av <avID>` |
| `database render` | `--av <avID> [--view <id>] [--query <q>] [-p N] [-s N]` |
| `database keys` | `--av <avID>` |
| `database key add` | `--av <id> --name <n> --type <t> [--icon <i>] [--prev <keyID>]` |
| `database key remove` | `--av <id> --key <keyID> [--remove-relation-dest]` |
| `database item add` | `--av <id> [--content <t>] [--block <id>] [--detached] [--group <id>] [--previous <itemID>] [--view <id>] [--ignore-default-fill]` |
| `database item update` | `--av <id> --key <keyID> --item <itemID> --value <json>` |
| `database item remove` | `--av <id> --ids id1,id2,...` |
| `database unused` / `database clean` | `database clean [--av <id>]` |

Key types: `text number date select mSelect url email phone mAsset template
created updated checkbox relation rollup lineNumber`.

## asset

| Command | Signature |
| --- | --- |
| `asset stat` | `--path <data-relative path>` |
| `asset unused` | list assets not referenced |
| `asset clean` | `[--path <single unused asset>]` |
| `asset upload` | `--id <target doc blockID> --file <local path>` (repeatable) |

## file (workspace-relative paths)

| Command | Signature |
| --- | --- |
| `file list` | `<path>` |
| `file find` | `<path> [--include <glob>] [--limit N]` |
| `file grep` | `--pattern <regex> --path <path> [--include <glob>] [--context N] [--limit N]` |
| `file read` | `<path>` |
| `file write` | `<path> [--file <src>]` (stdin default) |
| `file stat` | `<path>` |
| `file copy` | `<src> <dst>` |
| `file rename` | `<old> <new>` |
| `file delete` | `<path>` |

## history

| Command | Signature |
| --- | --- |
| `history list` | `[--notebook <id>] [--op delete\|update\|create] [-t 0-4] [-p N]` |
| `history search` | `<query>` (same flags) |
| `history get` | `--path <history path>` |
| `history rollback` | `--path <history path>` |
| `history clear` | clear all history |

Type `-t`: 0=doc-name 1=doc-content 2=asset 3=doc-id 4=database.

## repo (data snapshots)

| Command | Signature |
| --- | --- |
| `repo list` | `[-p N] [--tag]` |
| `repo create` | `[--memo <text>]` |
| `repo diff` | `--left <id> --right <id>` |
| `repo checkout` | `--id <snapshotID>` |
| `repo tag` / `repo untag` | `--id <id> --name <t>` / `--name <t>` |
| `repo search` | `<keyword> [-p N]` |
| `repo purge` | purge old snapshots |
| `repo file get` | `--id <fileID> [--output <file>]` (fileID is a content hash) |
| `repo file open` / `export` / `rollback` | `--id <fileID>` |

## template

| Command | Signature |
| --- | --- |
| `template search` | `[keyword]` |
| `template get` / `remove` | `--path <template path>` |
| `template create` | `--name <n> (--data \| --file) [--overwrite]` |
| `template save-as` | `--id <docID> --name <n> [--overwrite]` |
| `template render` | `--path <p> --id <blockID>` preview against a block |

## tag / bookmark

| Command | Signature |
| --- | --- |
| `tag list` | `[--keyword <k>]` |
| `tag rename` / `tag remove` | `--old <l> --new <l>` / `--label <l>` |
| `bookmark list` | list bookmarks |
| `bookmark labels` | list bookmark labels |
| `bookmark rename` / `bookmark remove` | `--old <l> --new <l>` / `--label <l>` |

## inbox (cloud clipped shorthands)

| Command | Signature |
| --- | --- |
| `inbox list` | `[-p N]` |
| `inbox get` | `--id <shorthandID>` |
| `inbox convert` | `--ids id1,id2,... --notebook <id> [--path </h/path>] [--remove-after]` |

## sync / system / serve

| Command | Signature |
| --- | --- |
| `sync status` / `sync pull` / `sync push` | cloud sync |
| `system current-time` | server time |
| `serve` | start HTTP kernel: `--port <p> [--workspace] [--readonly true] [--accessAuthCode <c>] [--ssl] [--lang <l>] [--mode dev\|prod] [--safe-mode] [--enable-pprof]` |

## shell completion

`siyuan completion bash|zsh|fish|powershell`.