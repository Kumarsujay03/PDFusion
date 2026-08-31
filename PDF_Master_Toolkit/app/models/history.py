"""Operation history and undo/redo support."""
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class OperationRecord:
    """Record of a single operation."""

    operation_type: str
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    input_files: list[str] = field(default_factory=list)
    output_files: list[str] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str = ""
    duration_seconds: float = 0.0


class HistoryManager:
    """Manages operation history with persistence."""

    def __init__(self, max_records: int = 1000) -> None:
        self._records: list[OperationRecord] = []
        self._max_records = max_records
        self._history_file = self._get_history_path()
        self._load()

    @staticmethod
    def _get_history_path() -> Path:
        app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
        history_dir = Path(app_data) / "PDFusion"
        history_dir.mkdir(parents=True, exist_ok=True)
        return history_dir / "history.json"

    def add_record(self, record: OperationRecord) -> None:
        """Add an operation record."""
        self._records.append(record)
        if len(self._records) > self._max_records:
            self._records = self._records[-self._max_records:]
        self._save()

    def get_records(self, limit: int = 50) -> list[OperationRecord]:
        """Get recent operation records."""
        return list(reversed(self._records[-limit:]))

    def get_records_by_type(self, operation_type: str) -> list[OperationRecord]:
        """Get records filtered by operation type."""
        return [r for r in self._records if r.operation_type == operation_type]

    def clear(self) -> None:
        """Clear all history."""
        self._records.clear()
        self._save()

    def _load(self) -> None:
        """Load history from file."""
        if self._history_file.exists():
            try:
                with open(self._history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._records = [OperationRecord(**r) for r in data]
            except (json.JSONDecodeError, TypeError):
                self._records = []

    def _save(self) -> None:
        """Save history to file."""
        with open(self._history_file, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self._records], f, indent=2)

    @property
    def record_count(self) -> int:
        return len(self._records)
