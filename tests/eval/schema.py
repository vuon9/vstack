"""Data model for execution traces (stdlib dataclasses).
Vendor-agnostic schema capturing interactions from Pi, OpenCode, or any
headless harness. Feed it with trace_extractor.py and assert invariants with
test_trace_invariants.py.

Timestamps are epoch milliseconds (int). Where a source log records none, the
extractor leaves them as None and Level-2 invariants that need timing
(W4 overlap) skip cleanly instead of guessing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TASK_TYPES = ("feature", "bugfix", "investigation")


@dataclass
class ToolCall:
    tool: str
    input: dict[str, Any] = field(default_factory=dict)
    output: str | None = None
    exit_code: int | None = None
    start_time_ms: int | None = None
    end_time_ms: int | None = None


@dataclass
class SubagentRun:
    subagent_id: str
    role: str
    prompt: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    final_output: str = ""
    start_time_ms: int | None = None
    end_time_ms: int | None = None


@dataclass
class TaskTrace:
    task_id: str = ""
    task_type: str = ""  # "feature" | "bugfix" | "investigation" | "parallel"
    repository: str = ""
    initial_prompt: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    subagents: list[SubagentRun] = field(default_factory=list)
    patch_diff: str = ""
    final_response: str = ""


# ---------------------------------------------------------------------------
# (De)serialization helpers
# ---------------------------------------------------------------------------


def to_dict(trace: TaskTrace) -> dict:
    return {
        "task_id": trace.task_id,
        "task_type": trace.task_type,
        "repository": trace.repository,
        "initial_prompt": trace.initial_prompt,
        "tool_calls": [tc.__dict__ for tc in trace.tool_calls],
        "subagents": [
            {
                "subagent_id": s.subagent_id,
                "role": s.role,
                "prompt": s.prompt,
                "tool_calls": [tc.__dict__ for tc in s.tool_calls],
                "final_output": s.final_output,
                "start_time_ms": s.start_time_ms,
                "end_time_ms": s.end_time_ms,
            }
            for s in trace.subagents
        ],
        "patch_diff": trace.patch_diff,
        "final_response": trace.final_response,
    }


def from_dict(data: dict) -> TaskTrace:
    trace = TaskTrace(
        task_id=data.get("task_id", ""),
        task_type=data.get("task_type", ""),
        repository=data.get("repository", ""),
        initial_prompt=data.get("initial_prompt", ""),
        patch_diff=data.get("patch_diff", ""),
        final_response=data.get("final_response", ""),
    )
    for tc in data.get("tool_calls", []):
        trace.tool_calls.append(ToolCall(**tc))
    for s in data.get("subagents", []):
        run = SubagentRun(
            subagent_id=s.get("subagent_id", ""),
            role=s.get("role", ""),
            prompt=s.get("prompt", ""),
            final_output=s.get("final_output", ""),
            start_time_ms=s.get("start_time_ms"),
            end_time_ms=s.get("end_time_ms"),
        )
        for tc in s.get("tool_calls", []):
            run.tool_calls.append(ToolCall(**tc))
        trace.subagents.append(run)
    return trace
