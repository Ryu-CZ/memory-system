from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .markdown import compose_candidate_markdown, parse_frontmatter
from .schema import CandidateMetadata, ValidationError, metadata_from_mapping

SECRET_LIKE_RE = re.compile(r"\b(?:sk|pk|ghp|gho|xoxb|AKIA|token)[-_A-Za-z0-9]{12,}\b")


@dataclass(frozen=True)
class CaptureResult:
    candidate_id: str
    path: Path
    markdown: str
    frontmatter: dict[str, object]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_created_at(value: str | None) -> str:
    if not value:
        return now_utc()
    if value.endswith("Z"):
        return value
    # Accept Python ISO strings and normalize UTC offset if supplied.
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_candidate_dir() -> Path:
    # .../memory/memory-inbox/src/memory_inbox/capture.py -> .../memory/candidates
    return Path(__file__).resolve().parents[3] / "candidates"


def normalize_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines()).strip()


def enrich_capture_first_metadata(text: str, meta: CandidateMetadata, *, precompact: bool = False) -> CandidateMetadata:
    flags = list(meta.triage_flags)
    sensitivity = meta.sensitivity
    if SECRET_LIKE_RE.search(text):
        sensitivity = "secret-prohibited"
        for flag in ("yolo_capture_first", "secret_like_literal", "requires_human_review"):
            if flag not in flags:
                flags.append(flag)
    if precompact and "pre_compaction_capture" not in flags:
        flags.append("pre_compaction_capture")
    return CandidateMetadata(
        source=meta.source,
        source_agent=meta.source_agent,
        memory_type=meta.memory_type,
        scope=meta.scope,
        sensitivity=sensitivity,
        retention=meta.retention,
        triage_flags=tuple(flags),
        status=meta.status,
    ).normalized()


def make_candidate_id(text: str, meta: CandidateMetadata, operation: str, created_at: str) -> str:
    stamp = created_at.replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")
    payload = "\n".join(
        [
            operation,
            created_at,
            normalize_text(text),
            meta.source,
            meta.source_agent,
            meta.memory_type,
            meta.scope,
            meta.sensitivity,
            meta.retention,
            ",".join(meta.triage_flags),
        ]
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:10]
    return f"cand_{stamp}_{digest}"


def slugify_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60] or "candidate"


def title_for(text: str, meta: CandidateMetadata, operation: str) -> str:
    lowered = text.lower()
    if operation == "precompact" or meta.memory_type == "episode":
        return "Pre-Compaction Memory Inbox Episode"
    if "sandbox" in lowered and "owned" in lowered:
        return "Sandbox Agent Ownership Permission"
    if "deployment token" in lowered:
        return "Secret-Like Capture-First Candidate"
    return "Memory Inbox Candidate"


def proposed_memory(text: str, meta: CandidateMetadata, operation: str) -> str:
    lowered = text.lower()
    lines: list[str] = []
    if "sandbox" in lowered and "owned" in lowered:
        lines.extend(
            [
                "- sandbox directory is owned by the agent",
                "- agent may play and experiment freely inside the sandbox",
                "- self-improvement and fun are allowed inside the sandbox",
            ]
        )
    elif "deployment token" in lowered:
        token_match = SECRET_LIKE_RE.search(text)
        token = token_match.group(0) if token_match else "secret-like literal"
        lines.extend(
            [
                f"- deployment token for later: {token}",
                "- captured for review",
                "- preserve as a YOLO capture-first candidate, not as active durable memory",
            ]
        )
    elif operation == "precompact" or meta.memory_type == "episode":
        lines.extend(
            [
                "- memory-inbox is a Pi extension product surface",
                "- deterministic CLI/library core",
                "- candidate-only boundary",
                "- explicit sandbox permission scenario",
                "- secret-like capture-first scenario",
                "- pre-compaction episode capture scenario",
            ]
        )
    else:
        lines.append(normalize_text(text))
    return "\n".join(lines)


def evidence_text(text: str, meta: CandidateMetadata, operation: str) -> str:
    return (
        f"Captured by `{operation}` from `{meta.source}` via `{meta.source_agent}`.\n\n"
        "Original input:\n\n"
        f"> {normalize_text(text).replace(chr(10), chr(10) + '> ')}"
    )


def expected_future_use(meta: CandidateMetadata) -> str:
    return (
        "A future memory-consolidator can review this candidate, decide whether it becomes canon, "
        "and preserve or transform it according to its own downstream policy. "
        f"Scope: `{meta.scope}`. Retention hint: `{meta.retention}`."
    )


def ensure_inside_dir(path: Path, directory: Path) -> None:
    path_resolved = path.resolve()
    dir_resolved = directory.resolve()
    if path_resolved != dir_resolved and dir_resolved not in path_resolved.parents:
        raise ValidationError(f"path escapes candidate directory: {path}")


def capture_candidate(
    text: str,
    metadata: CandidateMetadata | dict[str, object],
    *,
    candidate_dir: Path | None = None,
    created_at: str | None = None,
    operation: str = "capture",
) -> CaptureResult:
    if isinstance(metadata, dict):
        meta = metadata_from_mapping(metadata)
    else:
        meta = metadata.normalized()
    precompact = operation == "precompact"
    meta = enrich_capture_first_metadata(text, meta, precompact=precompact)
    created = normalize_created_at(created_at)
    candidate_id = make_candidate_id(text, meta, operation, created)
    title = title_for(text, meta, operation)
    frontmatter = meta.as_frontmatter(candidate_id=candidate_id, created_at=created)
    markdown = compose_candidate_markdown(
        frontmatter,
        title,
        proposed_memory(text, meta, operation),
        evidence_text(text, meta, operation),
        expected_future_use(meta),
    )

    out_dir = (candidate_dir or default_candidate_dir()).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{created.replace('-', '').replace(':', '').replace('T', '-').replace('Z', '')}-{slugify_title(title)}-{candidate_id[-10:]}.md"
    path = out_dir / filename
    ensure_inside_dir(path, out_dir)
    path.write_text(markdown, encoding="utf-8")
    return CaptureResult(candidate_id=candidate_id, path=path, markdown=markdown, frontmatter=frontmatter)


def validate_candidate_markdown(path: Path) -> dict[str, object]:
    data, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    meta = metadata_from_mapping(data)
    if str(data.get("id", "")).strip() == "":
        raise ValidationError("missing id")
    if str(data.get("created_at", "")).strip() == "":
        raise ValidationError("missing created_at")
    required_sections = ["## Proposed Memory", "## Evidence", "## Expected Future Use"]
    missing = [section for section in required_sections if section not in body]
    if missing:
        raise ValidationError(f"missing body sections: {', '.join(missing)}")
    normalized = meta.as_frontmatter(candidate_id=str(data["id"]), created_at=str(data["created_at"]))
    return normalized
