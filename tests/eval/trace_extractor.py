#!/usr/bin/env python3
"""Convert raw harness logs into the TaskTrace schema (tests/eval/schema.py).

Supports two input kinds:

1. A pi session transcript (NDJSON "session" records): the parent session file
   (messages with toolCall/toolResult pairs and custom_message subagent-notify
   records). This is the primary source. Timestamps are ISO strings on each
   record; tool stdout comes from toolResult message content.

2. A pi activity run.log (NDJSON "background-task-activity" records): fallback
   with no timestamps and truncated argsSummary only. Use it only when no
   session transcript exists; timing-dependent invariants (W4) will be skipped.

Child transcripts under subagent-artifacts/*.jsonl (recordType tool_start/
tool_end with epoch-ms ts) can be supplied via --artifacts-dir to enrich the
parent view with per-child timing and tool calls.

Usage:
  python3 tests/eval/trace_extractor.py <session.jsonl> \
      [--task-type feature|bugfix|investigation|parallel] \
      [--task-id NAME] [--patch-diff PATH] [--artifacts-dir DIR] \
      [--output out.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

if __package__ in (None, ""):
    # Allow running as a plain script: python3 tests/eval/trace_extractor.py
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.eval.schema import SubagentRun, TaskTrace, ToolCall


def _iso_to_ms(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).rstrip("Z")
    if "." in text:
        text = text.split(".", 1)[0]  # drop sub-second precision
    try:
        dt = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S")
        return int(dt.timestamp() * 1000)
    except ValueError:
        return None


def _read_jsonl(path: Path) -> list[dict]:
    records = []
    for line in path.open(encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _content_text(content) -> str:
    """Join text blocks of a message content list."""
    parts = []
    if isinstance(content, list):
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "text"
                and isinstance(block.get("text"), str)
            ):
                parts.append(block["text"])
    return "\n".join(parts)


def extract_from_session(path: Path, artifacts_dir: Path | None) -> TaskTrace:
    records = _read_jsonl(path)
    trace = TaskTrace(repository=str(path.parent))
    pending: dict = {}  # toolCallId -> ToolCall

    for rec in records:
        if rec.get("type") == "session":
            trace.task_id = rec.get("id", "")
            trace.repository = rec.get("cwd") or str(path.parent)
        elif rec.get("type") == "message":
            msg = rec.get("message", {})
            role = msg.get("role")
            if role == "user":
                if not trace.initial_prompt:
                    trace.initial_prompt = _content_text(msg.get("content"))
            elif role == "assistant":
                ts = _iso_to_ms(rec.get("timestamp"))
                for block in msg.get("content", []):
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "toolCall":
                        call = ToolCall(
                            tool=block.get("name", ""),
                            input=block.get("arguments") or {},
                            start_time_ms=ts,
                        )
                        pending[block.get("id", "")] = call
                        trace.tool_calls.append(call)
                    elif block.get("type") == "text" and block.get("text"):
                        trace.final_response += block["text"] + "\n"
            elif role == "toolResult":
                call = pending.pop(msg.get("toolCallId", ""), None)
                if call is None:
                    continue
                call.output = _content_text(msg.get("content"))
                call.exit_code = 0 if not msg.get("isError") else 1
                call.end_time_ms = _iso_to_ms(rec.get("timestamp")) or _iso_to_ms(
                    msg.get("timestamp")
                )
        elif rec.get("type") == "custom_message":
            if rec.get("customType") == "subagent-notify":
                content = rec.get("content", "")
                trace.subagents.append(
                    SubagentRun(
                        subagent_id="parent-notify",
                        role="reviewer/other",
                        prompt="",
                        final_output=content,
                    )
                )

    _enrich_from_artifacts(trace, artifacts_dir)
    return trace


def _enrich_from_artifacts(trace: TaskTrace, artifacts_dir: Path | None) -> None:
    """Merge child timing from subagent-artifacts transcripts when available."""
    if not artifacts_dir or not artifacts_dir.is_dir():
        return
    for child in sorted(artifacts_dir.glob("*_transcript.jsonl")):
        parts = child.name.split("_")
        role = parts[1] if len(parts) > 1 else "worker"
        run = SubagentRun(subagent_id=child.stem, role=role)
        open_calls: dict = {}
        starts, ends = [], []
        for rec in _read_jsonl(child):
            ts = rec.get("ts") or _iso_to_ms(rec.get("timestamp"))
            rt = rec.get("recordType")
            if rt == "tool_start":
                call = ToolCall(
                    tool=rec.get("toolName", ""),
                    input={
                        "command": rec.get("argsPreview")
                        or rec.get("argsPayload")
                        or ""
                    },
                    start_time_ms=ts,
                )
                cid = rec.get("toolCallId", "")
                open_calls[cid] = call
                run.tool_calls.append(call)
                if ts is not None:
                    starts.append(ts)
            elif rt == "tool_end":
                cid = rec.get("toolCallId", "")
                call = open_calls.pop(cid, None)
                if call is not None:
                    call.end_time_ms = ts
                    call.exit_code = 0 if not rec.get("isError") else 1
                if ts is not None:
                    ends.append(ts)
            elif rt == "message" and rec.get("sourceEventType") == "message_end":
                run.final_output = rec.get("text", "") or ""
        if starts:
            run.start_time_ms = min(starts)
        if ends:
            run.end_time_ms = max(ends)
        trace.subagents.append(run)


def extract_from_activity(path: Path) -> TaskTrace:
    """Fallback: parse a background-task-activity run.log (no timestamps)."""
    records = _read_jsonl(path)
    trace = TaskTrace(repository=str(path.parent), task_id=path.stem)
    for rec in records:
        kind = rec.get("kind")
        if kind == "tool_start":
            trace.tool_calls.append(
                ToolCall(
                    tool=rec.get("tool", ""),
                    input={"argsSummary": rec.get("argsSummary", "")},
                )
            )
        elif kind == "assistant_text":
            text = rec.get("text", "")
            if text:
                trace.final_response += text + "\n"
    return trace


def extract(path: Path, **kwargs) -> TaskTrace:
    path = Path(path)
    records = _read_jsonl(path)
    is_session = any(r.get("type") == "session" for r in records[:3])
    if is_session:
        trace = extract_from_session(path, kwargs.get("artifacts_dir"))
    else:
        trace = extract_from_activity(path)
    if kwargs.get("task_type"):
        trace.task_type = kwargs["task_type"]
    if kwargs.get("task_id"):
        trace.task_id = kwargs["task_id"]
    if kwargs.get("patch_diff"):
        trace.patch_diff = Path(kwargs["patch_diff"]).read_text(
            encoding="utf-8", errors="replace"
        )
    return trace


def main():
    parser = argparse.ArgumentParser(
        description="Convert harness logs to TaskTrace JSON."
    )
    parser.add_argument("input", help="session .jsonl or activity run.log")
    parser.add_argument(
        "--task-type", choices=["feature", "bugfix", "investigation", "parallel"]
    )
    parser.add_argument("--task-id", default="")
    parser.add_argument(
        "--patch-diff", default="", help="file containing the task patch diff"
    )
    parser.add_argument(
        "--artifacts-dir", default="", help="dir with subagent-artifacts transcripts"
    )
    parser.add_argument(
        "--output", default="", help="write JSON here instead of stdout"
    )
    args = parser.parse_args()

    artifacts = Path(args.artifacts_dir) if args.artifacts_dir else None
    trace = extract(
        Path(args.input),
        task_type=args.task_type,
        task_id=args.task_id,
        patch_diff=args.patch_diff,
        artifacts_dir=artifacts,
    )
    data = __import__("schema").to_dict(trace)
    if args.output:
        Path(args.output).write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {args.output}")
    else:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
