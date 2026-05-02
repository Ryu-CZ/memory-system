from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "memory" / "memory-inbox" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from memory_inbox.pi_adapter import (  # noqa: E402,F401
    handle_slash_command,
    memory_inbox_capture,
    memory_inbox_list,
    memory_inbox_precompact,
    session_before_compact,
)
