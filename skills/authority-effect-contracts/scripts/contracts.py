from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any


class ContractError(ValueError):
    pass


MANIFEST_FIELDS = {
    "schema_version", "manifest_id", "task_id", "task", "may", "must_not", "targets",
    "ask_before", "verification", "stop_on", "valid_until",
}
RECEIPT_FIELDS = {
    "schema_version", "receipt_id", "effect_status", "evidence_completeness",
    "target", "operation", "acting_surface", "observed_at",
    "verification_evidence", "sensitive_payload_retained",
}
EVIDENCE_FIELDS = {"kind", "handle", "observed_result"}
EFFECT_STATES = {
    "requested", "prepared", "attempted", "observed_succeeded",
    "observed_failed", "unknown",
}
EVIDENCE_COMPLETENESS = {"complete", "partial", "unknown"}
EVIDENCE_KINDS = {
    "artifact_sha256", "read_back", "immutable_handle", "tool_receipt",
    "http_read_back", "remote_object_id",
}
SENSITIVE_KEY = re.compile(r"(?:password|passwd|secret|token|api[_-]?key|private[_-]?key)", re.I)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject ambiguous objects at every depth before contract validation."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a JSON object")
    return value


def _exact_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        raise ContractError(f"{label} missing fields: {missing}")
    if unknown:
        raise ContractError(f"{label} unknown fields: {unknown}")


def _text(value: Any, field: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value


def _strings(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ContractError(f"{field} must be an array of non-empty strings")
    if len(value) != len(set(value)):
        raise ContractError(f"{field} must not contain duplicates")
    return value


def _timestamp(value: Any, field: str, *, nullable: bool = False) -> datetime | None:
    text = _text(value, field, nullable=nullable)
    if text is None:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{field} must include a timezone")
    return parsed


def validate_authority_manifest(value: Any, *, require_active: bool = False) -> dict[str, Any]:
    obj = _object(value, "authority manifest")
    _exact_fields(obj, MANIFEST_FIELDS, "authority manifest")
    if obj["schema_version"] != "authority-manifest/v1":
        raise ContractError("unsupported authority manifest schema_version")
    for field in ("manifest_id", "task_id", "task"):
        _text(obj[field], field)
    for field in ("may", "must_not", "targets", "ask_before", "verification", "stop_on"):
        _strings(obj[field], field)
    expires_at = _timestamp(obj["valid_until"], "valid_until")
    if require_active and expires_at <= datetime.now(timezone.utc):
        raise ContractError("authority manifest is expired")
    overlap = set(obj["may"]) & set(obj["must_not"])
    if overlap:
        raise ContractError(f"actions cannot be both allowed and prohibited: {sorted(overlap)}")
    return obj


def check_authority_subset(parent: Any, child: Any) -> list[str]:
    p = validate_authority_manifest(parent)
    c = validate_authority_manifest(child)
    errors: list[str] = []
    if c["task_id"] != p["task_id"]:
        errors.append("child task_id differs from parent")
    if not set(c["may"]).issubset(p["may"]):
        errors.append(f"child may expands parent: {sorted(set(c['may']) - set(p['may']))}")
    if not set(c["targets"]).issubset(p["targets"]):
        errors.append(f"child targets expand parent: {sorted(set(c['targets']) - set(p['targets']))}")
    for field in ("must_not", "ask_before", "verification", "stop_on"):
        missing = sorted(set(p[field]) - set(c[field]))
        if missing:
            errors.append(f"child {field} drops parent requirements: {missing}")
    if _timestamp(c["valid_until"], "valid_until") > _timestamp(p["valid_until"], "valid_until"):
        errors.append("child valid_until exceeds parent")
    now = datetime.now(timezone.utc)
    if _timestamp(p["valid_until"], "valid_until") <= now:
        errors.append("parent authority manifest is expired")
    if _timestamp(c["valid_until"], "valid_until") <= now:
        errors.append("child authority manifest is expired")
    return errors


def validate_effect_receipt(value: Any) -> dict[str, Any]:
    obj = _object(value, "effect receipt")
    _exact_fields(obj, RECEIPT_FIELDS, "effect receipt")
    if obj["schema_version"] != "external-effect-receipt/v1":
        raise ContractError("unsupported effect receipt schema_version")
    for field in ("receipt_id", "target", "operation"):
        _text(obj[field], field)
    if not isinstance(obj["effect_status"], str) or obj["effect_status"] not in EFFECT_STATES:
        raise ContractError(f"effect_status must be one of {sorted(EFFECT_STATES)}")
    if not isinstance(obj["evidence_completeness"], str) or obj["evidence_completeness"] not in EVIDENCE_COMPLETENESS:
        raise ContractError(f"evidence_completeness must be one of {sorted(EVIDENCE_COMPLETENESS)}")
    surface = _text(obj["acting_surface"], "acting_surface", nullable=True)
    observed_at = _timestamp(obj["observed_at"], "observed_at", nullable=True)
    if not isinstance(obj["verification_evidence"], list):
        raise ContractError("verification_evidence must be an array")
    for index, item in enumerate(obj["verification_evidence"]):
        evidence = _object(item, f"verification_evidence[{index}]")
        _exact_fields(evidence, EVIDENCE_FIELDS, f"verification_evidence[{index}]")
        for field in EVIDENCE_FIELDS:
            _text(evidence[field], f"verification_evidence[{index}].{field}")
        if evidence["kind"] not in EVIDENCE_KINDS:
            raise ContractError(
                f"verification_evidence[{index}].kind must be one of {sorted(EVIDENCE_KINDS)}"
            )
    if obj["sensitive_payload_retained"] is not False:
        raise ContractError("sensitive_payload_retained must be false")
    for key in obj:
        if key != "sensitive_payload_retained" and SENSITIVE_KEY.search(key):
            raise ContractError(f"sensitive field is prohibited: {key}")
    status = obj["effect_status"]
    if observed_at is not None and observed_at > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ContractError("observed_at cannot be future-dated beyond five minutes of clock skew")
    if status in {"attempted", "observed_succeeded", "observed_failed"} and (surface is None or observed_at is None):
        raise ContractError(f"{status} requires acting_surface and observed_at")
    if status == "observed_succeeded" and not obj["verification_evidence"]:
        raise ContractError("observed_succeeded requires verification_evidence")
    if status in {"requested", "prepared"} and obj["verification_evidence"]:
        raise ContractError(f"{status} must not include execution verification evidence")
    return obj
