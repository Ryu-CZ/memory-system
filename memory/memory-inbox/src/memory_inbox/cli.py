from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .candidates import list_candidates
from .capture import capture_candidate, validate_candidate_markdown
from .scenarios import parse_metadata_yaml, run_scenarios
from .schema import ValidationError, metadata_from_mapping

DEFAULT_CREATED_AT = "2026-04-27T00:00:00Z"


def read_input(args: argparse.Namespace) -> str:
    if getattr(args, "text", None):
        return args.text
    if getattr(args, "input_file", None):
        return Path(args.input_file).read_text(encoding="utf-8")
    return sys.stdin.read()


def read_metadata(args: argparse.Namespace, *, operation: str) -> dict[str, object]:
    if getattr(args, "metadata_file", None):
        return parse_metadata_yaml(Path(args.metadata_file).read_text(encoding="utf-8"))
    flags = list(args.triage_flag or [])
    if operation == "precompact" and "pre_compaction_capture" not in flags:
        flags.append("pre_compaction_capture")
    return {
        "source": args.source or ("agent_summary" if operation == "precompact" else "user_explicit"),
        "source_agent": args.source_agent,
        "memory_type": args.memory_type or ("episode" if operation == "precompact" else "project_context"),
        "scope": args.scope,
        "sensitivity": args.sensitivity,
        "retention": args.retention or ("review_by" if operation == "precompact" else "session_only"),
        "triage_flags": flags,
    }


def add_capture_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", help="input text to capture; stdin is used when omitted")
    parser.add_argument("--input-file", help="file containing input text")
    parser.add_argument("--metadata-file", help="simple YAML metadata file")
    parser.add_argument("--candidate-dir", type=Path, help="candidate output directory")
    parser.add_argument("--created-at", help="fixed ISO timestamp for deterministic output")
    parser.add_argument("--source", choices=sorted({"user_explicit", "observed", "imported", "inferred", "agent_summary", "subagent_summary", "tool_output"}))
    parser.add_argument("--source-agent", default="main-agent")
    parser.add_argument("--memory-type", choices=sorted({"project_context", "procedure", "decision", "episode", "source", "preference", "governance"}))
    parser.add_argument("--scope", default="project:/home/trval/projects/chats/pi_sandbox")
    parser.add_argument("--sensitivity", default="ordinary", choices=sorted({"ordinary", "personal", "sensitive", "secret-prohibited"}))
    parser.add_argument("--retention", choices=sorted({"indefinite", "review_by", "expire_by", "session_only"}))
    parser.add_argument("--triage-flag", action="append", default=[])


def cmd_capture(args: argparse.Namespace, *, operation: str = "capture") -> int:
    text = read_input(args)
    metadata = read_metadata(args, operation=operation)
    result = capture_candidate(
        text,
        metadata_from_mapping(metadata),
        candidate_dir=args.candidate_dir,
        created_at=args.created_at,
        operation=operation,
    )
    print(result.path)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    data = validate_candidate_markdown(Path(args.candidate_file))
    print(f"valid {data['id']}")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    created_at = args.created_at or DEFAULT_CREATED_AT
    tmp_output = Path(args.tmp_output)
    results = run_scenarios(Path(args.scenarios), tmp_output, created_at=created_at)
    ok = True
    for result in results:
        if result.ok:
            print(f"PASS {result.scenario_id}")
        else:
            ok = False
            print(f"FAIL {result.scenario_id}: {result.message}")
    return 0 if ok else 1


def cmd_list(args: argparse.Namespace) -> int:
    summaries = [summary.as_dict() for summary in list_candidates(args.candidate_dir)]
    if args.json:
        print(json.dumps(summaries, indent=2, sort_keys=True))
    else:
        for summary in summaries:
            print(f"{summary.get('id', '<missing-id>')}\t{summary.get('status', '<missing-status>')}\t{summary.get('memory_type', '<missing-type>')}\t{summary.get('path')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory-inbox")
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture", help="capture one candidate Markdown record")
    add_capture_args(capture)
    capture.set_defaults(func=lambda args: cmd_capture(args, operation="capture"))

    precompact = sub.add_parser("precompact", help="capture a pre-compaction episode candidate")
    add_capture_args(precompact)
    precompact.set_defaults(func=lambda args: cmd_capture(args, operation="precompact"))

    validate = sub.add_parser("validate", help="validate a candidate Markdown file")
    validate.add_argument("candidate_file")
    validate.set_defaults(func=cmd_validate)

    evaluate = sub.add_parser("eval", help="run repeatable scenario fixtures")
    evaluate.add_argument("--scenarios", required=True)
    evaluate.add_argument("--tmp-output", required=True)
    evaluate.add_argument("--created-at")
    evaluate.set_defaults(func=cmd_eval)

    list_cmd = sub.add_parser("list", help="list candidate Markdown records")
    list_cmd.add_argument("--candidate-dir", type=Path)
    list_cmd.add_argument("--json", action="store_true")
    list_cmd.set_defaults(func=cmd_list)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
