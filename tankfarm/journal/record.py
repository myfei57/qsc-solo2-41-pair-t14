"""Record value object carried by the append-only stream."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

SUBJECT_KEYS = ("tank_id", "valve_id", "pump_id", "batch_id", "latch", "subject")


@dataclass(frozen=True)
class Record:
    """One immutable entry of the operation stream."""

    seq: int
    record_id: str
    kind: str
    payload: Mapping[str, Any]
    ts: int

    @property
    def subject(self) -> str:
        """Equipment the record acts on, derived from its payload."""
        for key in SUBJECT_KEYS:
            value = self.payload.get(key)
            if isinstance(value, str) and value:
                return value
        return ""

    def as_payload(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "record_id": self.record_id,
            "kind": self.kind,
            "payload": dict(self.payload),
            "ts": self.ts,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "Record":
        return cls(
            seq=int(payload["seq"]),
            record_id=str(payload["record_id"]),
            kind=str(payload["kind"]),
            payload=dict(payload["payload"]),
            ts=int(payload["ts"]),
        )

