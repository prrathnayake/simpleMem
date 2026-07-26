#!/usr/bin/env python3
"""Command-line interface for the SimpleMem agent memory protocol."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .protocol import (
    DEFAULT_CONTEXT_BUDGET,
    build_context_bundle,
    finish_task,
    init_project,
    log_task,
    migrate,
    recall,
    reindex,
    start_task,
    status,
    validate,
)


def _payload(source: str | None) -> dict[str, Any]:
    if not source:
        return {}
    if source == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(source).read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON input: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("JSON input must be an object")
    return payload


def _print(value: Any, output_format: str = "json") -> None:
    if output_format == "json":
        print(json.dumps(value, indent=2, ensure_ascii=False))
    else:
        print(value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False))


def _project_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", type=Path, default=Path("."), help="Project root")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="simplemem", description="Universal project memory for agents")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Initialize .agent_memory")
    _project_parser(init)
    init.add_argument("--adapter", choices=["agents-md", "none"], default="agents-md")
    init.add_argument("--force", action="store_true", help="Refresh generated policy files only")

    start = commands.add_parser("start", help="Start or resume a task and return bounded context")
    _project_parser(start)
    start.add_argument("--task", required=True)
    start.add_argument("--input", help="JSON file, or - for stdin")
    start.add_argument("--query")
    start.add_argument("--budget", type=int, default=DEFAULT_CONTEXT_BUDGET)
    start.add_argument("--format", choices=["json", "markdown"], default="json")

    context = commands.add_parser("context", help="Build bounded project context")
    _project_parser(context)
    context.add_argument("query", nargs="?")
    context.add_argument("--budget", type=int, default=DEFAULT_CONTEXT_BUDGET)
    context.add_argument("--format", choices=["json", "markdown"], default="markdown")

    recall_parser = commands.add_parser("recall", help="Search long-term memory")
    _project_parser(recall_parser)
    recall_parser.add_argument("query")
    recall_parser.add_argument("--limit", type=int, default=8)
    recall_parser.add_argument("--format", choices=["json", "markdown"], default="json")

    reindex_parser = commands.add_parser(
        "reindex", help="Rebuild the deterministic content search index"
    )
    _project_parser(reindex_parser)

    log = commands.add_parser("log", help="Append structured task progress")
    _project_parser(log)
    log.add_argument("--task", required=True)
    log.add_argument("--status", required=True)
    log.add_argument("--input", help="JSON file, or - for stdin")

    finish = commands.add_parser("finish", help="Finish or hand off a task")
    _project_parser(finish)
    finish.add_argument("--task", required=True)
    finish.add_argument("--status", default="completed")
    finish.add_argument("--input", help="JSON file, or - for stdin")

    status_parser = commands.add_parser("status", help="Show memory status")
    _project_parser(status_parser)

    validation = commands.add_parser("validate", help="Validate protocol integrity")
    _project_parser(validation)
    validation.add_argument("--strict", action="store_true")
    validation.add_argument("--json", action="store_true", dest="as_json")

    migration = commands.add_parser("migrate", help="Safely migrate a legacy memory root")
    _project_parser(migration)
    migration.add_argument("--from", dest="source", default=".codex_memories")
    migration.add_argument("--apply", action="store_true")
    migration.add_argument("--finalize", action="store_true")
    migration.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            _print(init_project(args.project, force=args.force, adapter=args.adapter))
        elif args.command == "start":
            result = start_task(
                args.project,
                args.task,
                _payload(args.input),
                query=args.query,
                budget=args.budget,
            )
            _print(result if args.format == "json" else result["context"], args.format)
        elif args.command == "context":
            bundle = build_context_bundle(
                args.project, query=args.query, budget=args.budget
            )
            _print(
                {
                    "context": bundle.context,
                    "sources": bundle.sources,
                    "warnings": bundle.warnings,
                    "budget": bundle.budget,
                    "used": bundle.used,
                }
                if args.format == "json"
                else bundle.context,
                args.format,
            )
        elif args.command == "recall":
            results = [item.__dict__ for item in recall(args.project, args.query, limit=args.limit)]
            if args.format == "markdown":
                _print(
                    "\n".join(
                        f"- `{item['path']}` — {item['heading']} "
                        f"({item['score']}): {item['excerpt']}"
                        for item in results
                    ),
                    "markdown",
                )
            else:
                _print({"query": args.query, "results": results})
        elif args.command == "reindex":
            _print(reindex(args.project))
        elif args.command == "log":
            _print(log_task(args.project, args.task, args.status, _payload(args.input)))
        elif args.command == "finish":
            _print(finish_task(args.project, args.task, args.status, _payload(args.input)))
        elif args.command == "status":
            _print(status(args.project))
        elif args.command == "validate":
            result = validate(args.project, strict=args.strict)
            _print(result, "json" if args.as_json else "markdown")
            return 0 if result["valid"] else 1
        elif args.command == "migrate":
            if args.finalize and not args.apply:
                raise ValueError("--finalize requires --apply")
            result = migrate(
                args.project,
                args.source,
                apply=args.apply,
                finalize=args.finalize,
            )
            _print(result, "json" if args.as_json else "markdown")
        return 0
    except (OSError, ValueError) as exc:
        print(f"simplemem: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
