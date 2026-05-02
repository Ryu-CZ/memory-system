from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

SOURCES = {
    "user_explicit",
    "observed",
    "imported",
    "inferred",
    "agent_summary",
    "subagent_summary",
    "tool_output",
}

MEMORY_TYPES = {
    "project_context",
    "procedure",
    "decision",
    "episode",
    "source",
    "preference",
    "governance",
}

SENSITIVITIES = {
    "ordinary",
    "personal",
    "sensitive",
    "secret-prohibited",
}

RETENTIONS = {
    "indefinite",
    "review_by",
    "expire_by",
    "session_only",
}

STATUSES = {
    "candidate",
    "needs_review",
}

REQUIRED_FIELDS = {
    "source",
    "source_agent",
    "memory_type",
    "scope",
    "sensitivity",
    "retention",
}


class ValidationError(ValueError):
    """Raised when candidate metadata or frontmatter is invalid."""


@dataclass(frozen=True)
class CandidateMetadata:
    source: str
    source_agent: str
    memory_type: str
    scope: str
    sensitivity: str
    retention: str
    triage_flags: tuple[str, ...] = ()
    status: str | None = None

    def normalized(self) -> "CandidateMetadata":
        flags = tuple(dict.fromkeys(flag.strip() for flag in self.triage_flags if flag.strip()))
        sensitivity = self.sensitivity
        status = self.status
        if sensitivity == "secret-prohibited" or "requires_human_review" in flags:
            status = "needs_review"
        if not status:
            status = "candidate"
        normalized = CandidateMetadata(
            source=self.source.strip(),
            source_agent=self.source_agent.strip(),
            memory_type=self.memory_type.strip(),
            scope=self.scope.strip(),
            sensitivity=sensitivity.strip(),
            retention=self.retention.strip(),
            triage_flags=flags,
            status=status.strip(),
        )
        validate_metadata(normalized)
        return normalized

    def as_frontmatter(self, *, candidate_id: str, created_at: str) -> dict[str, object]:
        meta = self.normalized()
        return {
            "id": candidate_id,
            "status": meta.status,
            "created_at": created_at,
            "source": meta.source,
            "source_agent": meta.source_agent,
            "memory_type": meta.memory_type,
            "scope": meta.scope,
            "sensitivity": meta.sensitivity,
            "retention": meta.retention,
            "triage_flags": list(meta.triage_flags),
        }


def validate_metadata(meta: CandidateMetadata) -> None:
    missing = [name for name in REQUIRED_FIELDS if not getattr(meta, name)]
    if missing:
        raise ValidationError(f"missing required metadata: {', '.join(sorted(missing))}")
    if meta.source not in SOURCES:
        raise ValidationError(f"invalid source: {meta.source}")
    if meta.memory_type not in MEMORY_TYPES:
        raise ValidationError(f"invalid memory_type: {meta.memory_type}")
    if not (meta.scope == "global" or meta.scope.startswith(("project:", "session:", "task:"))):
        raise ValidationError(f"invalid scope: {meta.scope}")
    if meta.sensitivity not in SENSITIVITIES:
        raise ValidationError(f"invalid sensitivity: {meta.sensitivity}")
    if meta.retention not in RETENTIONS:
        raise ValidationError(f"invalid retention: {meta.retention}")
    if meta.status and meta.status not in STATUSES:
        raise ValidationError(f"invalid status: {meta.status}")


def metadata_from_mapping(data: dict[str, object]) -> CandidateMetadata:
    flags_obj = data.get("triage_flags", [])
    if flags_obj is None:
        flags: Iterable[str] = []
    elif isinstance(flags_obj, str):
        flags = [flags_obj]
    else:
        flags = [str(item) for item in flags_obj]  # type: ignore[arg-type]
    return CandidateMetadata(
        source=str(data.get("source", "")).strip(),
        source_agent=str(data.get("source_agent", "")).strip(),
        memory_type=str(data.get("memory_type", "")).strip(),
        scope=str(data.get("scope", "")).strip(),
        sensitivity=str(data.get("sensitivity", "ordinary")).strip(),
        retention=str(data.get("retention", "session_only")).strip(),
        triage_flags=tuple(flags),
        status=str(data.get("status", "")).strip() or None,
    ).normalized()
