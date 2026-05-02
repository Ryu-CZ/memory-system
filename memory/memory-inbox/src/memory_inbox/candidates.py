from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .capture import default_candidate_dir
from .markdown import parse_frontmatter
from .schema import ValidationError, metadata_from_mapping


@dataclass(frozen=True)
class CandidateSummary:
    path: Path
    frontmatter: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"path": str(self.path), **self.frontmatter}


def list_candidates(candidate_dir: Path | None = None) -> list[CandidateSummary]:
    directory = (candidate_dir or default_candidate_dir()).resolve()
    if not directory.exists():
        return []
    if not directory.is_dir():
        raise ValidationError(f"candidate path is not a directory: {directory}")
    summaries: list[CandidateSummary] = []
    for path in sorted(directory.glob("*.md")):
        data, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
        metadata_from_mapping(data)
        summaries.append(CandidateSummary(path=path, frontmatter=data))
    return summaries
