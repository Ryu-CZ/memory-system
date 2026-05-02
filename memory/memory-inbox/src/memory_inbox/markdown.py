from __future__ import annotations

from typing import Any

from .schema import ValidationError


def dump_frontmatter(data: dict[str, Any]) -> str:
    lines: list[str] = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            if value:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: []")
        elif value is None:
            lines.append(f"{key}: null")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValidationError("candidate Markdown must start with YAML-like frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValidationError("candidate Markdown frontmatter is not closed")
    raw = text[4:end].strip("\n")
    body = text[end + len("\n---") :].lstrip("\n")
    data = parse_simple_yaml(raw)
    return data, body


def parse_simple_yaml(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_key is None:
                raise ValidationError(f"list item without key: {line}")
            data.setdefault(current_key, []).append(line[4:].strip())
            continue
        if ":" not in line:
            raise ValidationError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "[]":
            data[key] = []
        elif value == "null":
            data[key] = None
        elif value == "":
            data[key] = []
        else:
            data[key] = value
    return data


def compose_candidate_markdown(frontmatter: dict[str, Any], title: str, proposed: str, evidence: str, future_use: str) -> str:
    return (
        dump_frontmatter(frontmatter)
        + "\n"
        + f"# {title}\n\n"
        + "## Proposed Memory\n\n"
        + proposed.strip()
        + "\n\n"
        + "## Evidence\n\n"
        + evidence.strip()
        + "\n\n"
        + "## Expected Future Use\n\n"
        + future_use.strip()
        + "\n"
    )
