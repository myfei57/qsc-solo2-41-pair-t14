"""Query filters shared by the audit trail and the record stream."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

SUBJECT_KEYS = ("tank_id", "valve_id", "pump_id", "batch_id", "latch", "subject")


def subject_of(record: Any) -> str:
    """Best-effort subject of an audit entry or a stream record."""
    subject = getattr(record, "subject", None)
    if isinstance(subject, str):
        return subject
    payload = getattr(record, "payload", None)
    if isinstance(payload, Mapping):
        for key in SUBJECT_KEYS:
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
    return ""


@dataclass(frozen=True)
class RecordFilter:
    """Narrows a record set by kind, subject, sequence window and limit."""

    kinds: tuple[str, ...] = ()
    subject: str | None = None
    min_seq: int = 0
    max_seq: int = 0
    limit: int = 0

    def matches(self, record: Any) -> bool:
        if self.kinds and record.kind not in self.kinds:
            return False
        if self.subject is not None and subject_of(record) != self.subject:
            return False
        if self.min_seq and record.seq < self.min_seq:
            return False
        if self.max_seq and record.seq > self.max_seq:
            return False
        return True

    def apply(self, records: Sequence[Any]) -> tuple[Any, ...]:
        selected = tuple(record for record in records if self.matches(record))
        if self.limit:
            selected = selected[-self.limit :]
        return selected

    def as_payload(self) -> dict[str, Any]:
        return {
            "kinds": list(self.kinds),
            "subject": self.subject,
            "min_seq": self.min_seq,
            "max_seq": self.max_seq,
            "limit": self.limit,
        }
