from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .capture import capture_candidate
from .markdown import parse_frontmatter
from .schema import ValidationError, metadata_from_mapping


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    ok: bool
    message: str
    candidate_path: Path | None = None


def parse_simple_expected_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_section: str | None = None
    current_key: str | None = None
    nested_section: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0:
            key, _, value = stripped.partition(":")
            if value.strip():
                data[key] = coerce_scalar(value.strip())
                current_section = None
            else:
                data[key] = {}
                current_section = key
            current_key = None
            nested_section = None
        elif indent == 2 and current_section:
            key, _, value = stripped.partition(":")
            if value.strip():
                data[current_section][key] = coerce_scalar(value.strip())
                current_key = key
                nested_section = None
            else:
                data[current_section][key] = []
                current_key = key
                nested_section = current_section
        elif indent == 4 and stripped.startswith("- ") and current_section and current_key:
            data[current_section].setdefault(current_key, []).append(stripped[2:])
        elif indent == 4 and current_section:
            # Supports score: pass_requires: lists, though the evaluator does not need it yet.
            key, _, value = stripped.partition(":")
            if value.strip():
                data[current_section][key] = coerce_scalar(value.strip())
            else:
                data[current_section][key] = []
                current_key = key
                nested_section = current_section
        elif indent == 6 and stripped.startswith("- ") and nested_section and current_key:
            data[nested_section].setdefault(current_key, []).append(stripped[2:])
    return data


def coerce_scalar(value: str) -> Any:
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "null":
        return None
    if value == "[]":
        return []
    return value


def extract_input_text(input_md: str) -> str:
    in_quote = False
    lines: list[str] = []
    for line in input_md.splitlines():
        if line.startswith("> "):
            in_quote = True
            lines.append(line[2:])
        elif in_quote and line.startswith(">"):
            lines.append(line[1:].lstrip())
        elif in_quote:
            break
    if not lines:
        raise ValidationError("scenario input.md does not contain quoted input text")
    return "\n".join(lines).strip()


def extract_metadata(input_md: str) -> dict[str, Any]:
    marker = "## Caller Metadata"
    start = input_md.find(marker)
    if start == -1:
        raise ValidationError("scenario input.md missing Caller Metadata section")
    fence_start = input_md.find("```yaml", start)
    if fence_start == -1:
        raise ValidationError("scenario input.md missing yaml metadata block")
    fence_start += len("```yaml")
    fence_end = input_md.find("```", fence_start)
    if fence_end == -1:
        raise ValidationError("scenario input.md metadata block not closed")
    raw = input_md[fence_start:fence_end].strip("\n")
    return parse_metadata_yaml(raw)


def parse_metadata_yaml(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - "):
            if not current_key:
                raise ValidationError("metadata list item without key")
            data.setdefault(current_key, []).append(line[4:].strip())
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValidationError(f"invalid metadata line: {line}")
        key = key.strip()
        value = value.strip()
        current_key = key
        if value:
            data[key] = value
        else:
            data[key] = []
    return data


def operation_from_input(input_md: str) -> str:
    if "memory-inbox precompact" in input_md:
        return "precompact"
    return "capture"


def run_scenario(scenario_dir: Path, tmp_output: Path, *, created_at: str) -> ScenarioResult:
    scenario_id = scenario_dir.name
    try:
        input_md = (scenario_dir / "input.md").read_text(encoding="utf-8")
        expected = parse_simple_expected_yaml(scenario_dir / "expected.yaml")
        text = extract_input_text(input_md)
        metadata = extract_metadata(input_md)
        operation = operation_from_input(input_md)
        candidate_dir = tmp_output / scenario_id / "candidates"
        result = capture_candidate(text, metadata, candidate_dir=candidate_dir, created_at=created_at, operation=operation)
        candidate_files = sorted(candidate_dir.glob("*.md"))
        assert_equal(len(candidate_files), 1, "expected exactly one candidate file")
        frontmatter, body = parse_frontmatter(result.markdown)
        candidate_expected = expected["candidate"]
        for field in ["status", "memory_type", "scope", "sensitivity", "source", "source_agent", "retention"]:
            assert_equal(frontmatter.get(field), candidate_expected.get(field), f"frontmatter {field}")
        flags = set(frontmatter.get("triage_flags") or [])
        for flag in candidate_expected.get("required_triage_flags") or []:
            if flag not in flags:
                raise AssertionError(f"missing triage flag: {flag}")
        for phrase in candidate_expected.get("must_include") or []:
            if phrase not in result.markdown:
                raise AssertionError(f"missing required phrase: {phrase}")
        for phrase in candidate_expected.get("must_not_include") or []:
            if phrase in result.markdown:
                raise AssertionError(f"forbidden phrase present: {phrase}")
        forbidden = candidate_expected.get("forbidden_literals") or []
        for phrase in forbidden:
            if phrase in result.markdown:
                raise AssertionError(f"forbidden literal present: {phrase}")
        disallowed_suffixes = {".sqlite", ".sqlite3", ".db"}
        extra_files = [p for p in (tmp_output / scenario_id).rglob("*") if p.is_file() and p not in candidate_files]
        if any(p.suffix in disallowed_suffixes for p in extra_files):
            raise AssertionError(f"unexpected generated artifact: {extra_files}")
        return ScenarioResult(scenario_id, True, "PASS", result.path)
    except Exception as exc:  # noqa: BLE001 - CLI should report scenario assertion failures compactly.
        return ScenarioResult(scenario_id, False, str(exc), None)


def assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def run_scenarios(scenarios_dir: Path, tmp_output: Path, *, created_at: str) -> list[ScenarioResult]:
    scenario_dirs = sorted(path for path in scenarios_dir.iterdir() if path.is_dir())
    return [run_scenario(path, tmp_output, created_at=created_at) for path in scenario_dirs]
