#!/usr/bin/env python3
"""Normative executable validator for experimental context trial packets.

Validation establishes representation and internal consistency only. It does not
observe a runtime, run an orchestration trial, or prove task/source truth. The
paired JSON Schema is an informative interoperability representation; drift is a
release blocker.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "context-trial-packet/v1"
CONDITIONS = {"baseline", "append_shared", "typed_bounded"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class PacketDecodeError(ValueError):
    """JSON could not be decoded without ambiguity."""


def _reject_invalid_constant(value: str) -> Any:
    raise PacketDecodeError(f"invalid JSON constant: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PacketDecodeError(f"duplicate key: {key}")
        result[key] = value
    return result


def load_packet(path: str | Path) -> dict[str, Any]:
    """Load one JSON packet, rejecting duplicate keys and malformed roots."""
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            packet = json.load(
                handle,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_invalid_constant,
            )
    except (OSError, UnicodeError, json.JSONDecodeError, PacketDecodeError) as exc:
        raise PacketDecodeError(str(exc)) from exc
    if not isinstance(packet, dict):
        raise PacketDecodeError("packet root must be an object")
    return packet


def _object(
    value: Any,
    path: str,
    required: set[str],
    allowed: set[str],
    errors: list[str],
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return None
    for key in sorted(required - value.keys()):
        errors.append(f"{path}: missing required field {key}")
    for key in sorted(value.keys() - allowed):
        errors.append(f"{path}: unknown field {key}")
    return value


def _nonempty_string(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")


def _sha256(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        errors.append(f"{path} must be a lowercase 64-character SHA-256 digest")


def _unique_strings(values: Any, path: str, errors: list[str]) -> list[str] | None:
    if not isinstance(values, list) or not all(isinstance(item, str) and item for item in values):
        errors.append(f"{path} must be an array of non-empty strings")
        return None
    if len(values) != len(set(values)):
        errors.append(f"{path} values must be unique")
    return values


def _string_set(values: list[Any]) -> set[str]:
    return {value for value in values if isinstance(value, str)}


def _has_duplicate_strings(values: list[Any]) -> bool:
    strings = [value for value in values if isinstance(value, str)]
    return len(strings) != len(set(strings))


def _measurement(value: Any, path: str, errors: list[str], *,
                 allowed_units: tuple[str, ...] = ("bytes", "tokens")) -> dict[str, Any] | None:
    error_count = len(errors)
    obj = _object(
        value,
        path,
        {"kind", "unit", "method"},
        {"kind", "unit", "method", "value", "lower", "upper", "source"},
        errors,
    )
    if obj is None:
        return None
    kind = obj.get("kind")
    unit = obj.get("unit")
    method = obj.get("method")
    if kind not in ("exact", "range", "not_measured"):
        errors.append(f"{path}.kind must be exact, range, or not_measured")
    if unit not in allowed_units:
        errors.append(f"{path}.unit must be {' or '.join(allowed_units)}")
    _nonempty_string(method, f"{path}.method", errors)
    if "source" in obj:
        _nonempty_string(obj.get("source"), f"{path}.source", errors)

    if kind == "exact":
        if set(obj) & {"lower", "upper"}:
            errors.append(f"{path}: exact measurement cannot contain lower or upper")
        exact_value = obj.get("value")
        if (
            not isinstance(exact_value, (int, float))
            or isinstance(exact_value, bool)
            or not math.isfinite(exact_value)
            or exact_value < 0
        ):
            errors.append(f"{path}.value must be a finite non-negative number")
        elif unit in ("bytes", "tokens") and not isinstance(exact_value, int):
            errors.append(f"{path}.value exact bytes/tokens must be a non-negative integer")
        if unit == "tokens" and method != "runtime_tokenizer":
            errors.append(f"{path}: exact token measurements require method runtime_tokenizer")
        if unit == "bytes" and method != "utf8_byte_count":
            errors.append(f"{path}: exact byte measurements require method utf8_byte_count")
    elif kind == "range":
        if "value" in obj:
            errors.append(f"{path}: range measurement cannot contain value")
        lower, upper = obj.get("lower"), obj.get("upper")
        if not isinstance(lower, (int, float)) or isinstance(lower, bool) or not math.isfinite(lower) or lower < 0:
            errors.append(f"{path}.lower must be a finite non-negative number")
        if not isinstance(upper, (int, float)) or isinstance(upper, bool) or not math.isfinite(upper) or upper < 0:
            errors.append(f"{path}.upper must be a finite non-negative number")
        if unit in ("bytes", "tokens") and (
            not isinstance(lower, int) or isinstance(lower, bool)
            or not isinstance(upper, int) or isinstance(upper, bool)
        ):
            errors.append(f"{path}: range bytes/tokens bounds must be non-negative integers")
        if (
            isinstance(lower, (int, float)) and not isinstance(lower, bool) and math.isfinite(lower)
            and isinstance(upper, (int, float)) and not isinstance(upper, bool) and math.isfinite(upper)
            and lower > upper
        ):
            errors.append(f"{path}: lower must not exceed upper")
    elif kind == "not_measured":
        if set(obj) & {"value", "lower", "upper"}:
            errors.append(f"{path}: not_measured cannot contain numeric fields")
    return obj if len(errors) == error_count else None


def _bounds(measurement: dict[str, Any]) -> tuple[float, float] | None:
    if measurement.get("kind") == "exact" and isinstance(measurement.get("value"), (int, float)) and not isinstance(measurement.get("value"), bool) and math.isfinite(measurement["value"]):
        value = float(measurement["value"])
        return value, value
    if measurement.get("kind") == "range" and isinstance(measurement.get("lower"), (int, float)) and not isinstance(measurement.get("lower"), bool) and math.isfinite(measurement["lower"]) and isinstance(measurement.get("upper"), (int, float)) and not isinstance(measurement.get("upper"), bool) and math.isfinite(measurement["upper"]):
        return float(measurement["lower"]), float(measurement["upper"])
    return None


def _json_equal_strict(left: Any, right: Any) -> bool:
    """Compare JSON values recursively without Python bool/int coercion."""
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is bool and type(right) is bool and left is right
    if left is None or right is None:
        return left is None and right is None
    if isinstance(left, (int, float)) or isinstance(right, (int, float)):
        return (
            isinstance(left, (int, float)) and not isinstance(left, bool)
            and isinstance(right, (int, float)) and not isinstance(right, bool)
            and left == right
        )
    if isinstance(left, str) or isinstance(right, str):
        return isinstance(left, str) and isinstance(right, str) and left == right
    if isinstance(left, list) or isinstance(right, list):
        return (
            isinstance(left, list) and isinstance(right, list)
            and len(left) == len(right)
            and all(_json_equal_strict(a, b) for a, b in zip(left, right))
        )
    if isinstance(left, dict) or isinstance(right, dict):
        return (
            isinstance(left, dict) and isinstance(right, dict)
            and left.keys() == right.keys()
            and all(_json_equal_strict(left[key], right[key]) for key in left)
        )
    return False


def validate_packet(packet: dict[str, Any]) -> list[str]:
    """Return schema and consistency defects; empty means structurally valid."""
    errors: list[str] = []
    top_required = {"schema_version", "trial_id", "task", "acceptance_truths", "required_branches", "conditions", "final_disposition", "limitations"}
    top = _object(packet, "$", top_required, top_required, errors)
    if top is None:
        return errors
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    _nonempty_string(packet.get("trial_id"), "$.trial_id", errors)

    task = _object(packet.get("task"), "$.task", {"task_id", "task_version", "task_manifest_sha256", "family", "case_kind"}, {"task_id", "task_version", "task_manifest_sha256", "family", "case_kind"}, errors)
    if task:
        for key in ("task_id", "task_version", "family", "case_kind"):
            _nonempty_string(task.get(key), f"$.task.{key}", errors)
        _sha256(task.get("task_manifest_sha256"), "$.task.task_manifest_sha256", errors)

    truth_ids: list[Any] = []
    expected_by_truth_id: dict[str, Any] = {}
    truths = packet.get("acceptance_truths")
    if not isinstance(truths, list) or not truths:
        errors.append("$.acceptance_truths must be a non-empty array")
    else:
        for index, truth in enumerate(truths):
            path = f"$.acceptance_truths[{index}]"
            obj = _object(truth, path, {"truth_id", "statement", "expected"}, {"truth_id", "statement", "expected"}, errors)
            if obj:
                _nonempty_string(obj.get("truth_id"), f"{path}.truth_id", errors)
                _nonempty_string(obj.get("statement"), f"{path}.statement", errors)
                truth_id = obj.get("truth_id")
                truth_ids.append(truth_id)
                if isinstance(truth_id, str):
                    expected_by_truth_id[truth_id] = obj.get("expected")
        if _has_duplicate_strings(truth_ids):
            errors.append("acceptance truth_id values must be unique")

    required_branches = _unique_strings(packet.get("required_branches"), "$.required_branches", errors) or []
    if not required_branches:
        errors.append("$.required_branches must name at least one required branch")

    conditions = packet.get("conditions")
    condition_names: list[Any] = []
    condition_ids: list[Any] = []
    condition_manifest_hashes: list[Any] = []
    condition_by_name: dict[str, dict[str, Any]] = {}
    if not isinstance(conditions, list):
        errors.append("$.conditions must be an array")
        conditions = []
    for index, raw_condition in enumerate(conditions):
        path = f"$.conditions[{index}]"
        required = {"condition_id", "condition", "prompt_sha256", "condition_manifest_sha256", "runtime", "context", "acceptance_results", "branches", "costs", "hard_gate_defects", "disposition"}
        condition = _object(raw_condition, path, required, required, errors)
        if condition is None:
            continue
        name = condition.get("condition")
        condition_names.append(name)
        condition_ids.append(condition.get("condition_id"))
        condition_manifest_hashes.append(condition.get("condition_manifest_sha256"))
        if isinstance(name, str):
            condition_by_name[name] = condition
        _nonempty_string(condition.get("condition_id"), f"{path}.condition_id", errors)
        _sha256(condition.get("prompt_sha256"), f"{path}.prompt_sha256", errors)
        _sha256(condition.get("condition_manifest_sha256"), f"{path}.condition_manifest_sha256", errors)

        runtime_fields = {"provider", "model", "runtime", "observed_usable_capacity", "capacity_observation_status", "capacity_source", "truncation_compaction_behavior", "retrieval_behavior"}
        runtime = _object(condition.get("runtime"), f"{path}.runtime", runtime_fields, runtime_fields, errors)
        runtime_capacity = None
        capacity_observation_status = None
        if runtime:
            for key in ("provider", "model", "runtime", "capacity_source", "truncation_compaction_behavior", "retrieval_behavior"):
                _nonempty_string(runtime.get(key), f"{path}.runtime.{key}", errors)
            runtime_capacity = _measurement(runtime.get("observed_usable_capacity"), f"{path}.runtime.observed_usable_capacity", errors)
            capacity_observation_status = runtime.get("capacity_observation_status")
            if capacity_observation_status not in ("observed", "not_observed"):
                errors.append(f"{path}.runtime.capacity_observation_status must be observed or not_observed")
            if capacity_observation_status == "observed" and runtime_capacity and runtime_capacity.get("kind") == "not_measured":
                errors.append(f"{path}.runtime.observed_usable_capacity must be observed, not not_measured")

        context_required = {"rendered_prompt", "input_artifacts", "tool_output_reserve", "verification_reserve", "peak_rendered_context", "context_fit"}
        context_allowed = context_required | {"observed_limit", "margin"}
        context = _object(condition.get("context"), f"{path}.context", context_required, context_allowed, errors)
        context_measurements: dict[str, dict[str, Any]] = {}
        if context:
            for key in ("rendered_prompt", "input_artifacts", "tool_output_reserve", "verification_reserve", "peak_rendered_context"):
                measured = _measurement(context.get(key), f"{path}.context.{key}", errors)
                if measured:
                    context_measurements[key] = measured
            for key in ("observed_limit", "margin"):
                if key in context:
                    measured = _measurement(context.get(key), f"{path}.context.{key}", errors)
                    if measured:
                        context_measurements[key] = measured
            fit = context.get("context_fit")
            if not isinstance(fit, bool):
                errors.append(f"{path}.context.context_fit must be boolean")
            if fit:
                if capacity_observation_status != "observed":
                    errors.append(f"{path}.context: context_fit=true requires capacity_observation_status=observed")
                fit_keys = (
                    "rendered_prompt", "input_artifacts", "peak_rendered_context",
                    "tool_output_reserve", "verification_reserve", "observed_limit", "margin",
                )
                for key in ("observed_limit", "margin"):
                    if key not in context:
                        errors.append(f"{path}.context: context_fit=true requires {key}")
                for key in fit_keys:
                    measurement = context_measurements.get(key)
                    if measurement is None or _bounds(measurement) is None:
                        errors.append(f"{path}.context: context_fit=true requires measured {key}")
                measured_capacity = [
                    context_measurements.get(key) for key in fit_keys
                ] + [runtime_capacity]
                if all(measurement is not None and _bounds(measurement) is not None for measurement in measured_capacity):
                    assert runtime_capacity is not None
                    units = {
                        measurement.get("unit")
                        for measurement in measured_capacity
                        if measurement and isinstance(measurement.get("unit"), str)
                    }
                    if len(units) != 1:
                        errors.append(f"{path}.context: context-fit measurements must use the same unit")
                    rendered_bounds = _bounds(context_measurements["rendered_prompt"])
                    input_bounds = _bounds(context_measurements["input_artifacts"])
                    peak_bounds = _bounds(context_measurements["peak_rendered_context"])
                    tool_bounds = _bounds(context_measurements["tool_output_reserve"])
                    verification_bounds = _bounds(context_measurements["verification_reserve"])
                    limit_bounds = _bounds(context_measurements["observed_limit"])
                    margin_bounds = _bounds(context_measurements["margin"])
                    runtime_bounds = _bounds(runtime_capacity)
                    if (
                        runtime_capacity.get("unit") != context_measurements["observed_limit"].get("unit")
                        or runtime_bounds != limit_bounds
                    ):
                        errors.append(
                            f"{path}.context.observed_limit must match runtime observed_usable_capacity units and bounds"
                        )
                    assert rendered_bounds and input_bounds and peak_bounds and tool_bounds and verification_bounds and limit_bounds and margin_bounds
                    if len(units) == 1:
                        component_upper = rendered_bounds[1] + input_bounds[1]
                        if peak_bounds[0] < component_upper:
                            errors.append(
                                f"{path}.context: peak lower bound must cover rendered prompt and input artifact upper bounds"
                            )
                        used_lower = peak_bounds[0] + tool_bounds[0] + verification_bounds[0]
                        used_upper = peak_bounds[1] + tool_bounds[1] + verification_bounds[1]
                        if used_upper > limit_bounds[0]:
                            errors.append(
                                f"{path}.context: peak plus reserves exceeds the conservative observed limit"
                            )
                        else:
                            derived_margin = (
                                limit_bounds[0] - used_upper,
                                limit_bounds[1] - used_lower,
                            )
                            if margin_bounds != derived_margin:
                                errors.append(
                                    f"{path}.context: declared margin bounds must match the derived capacity range"
                                )

        results = condition.get("acceptance_results")
        result_ids: list[Any] = []
        all_truths_pass = True
        if not isinstance(results, list):
            errors.append(f"{path}.acceptance_results must be an array")
            results = []
        for result_index, raw_result in enumerate(results):
            result_path = f"{path}.acceptance_results[{result_index}]"
            result = _object(raw_result, result_path, {"truth_id", "observed", "passed", "evidence"}, {"truth_id", "observed", "passed", "evidence"}, errors)
            if result:
                result_truth_id = result.get("truth_id")
                result_ids.append(result_truth_id)
                _nonempty_string(result_truth_id, f"{result_path}.truth_id", errors)
                if not isinstance(result.get("passed"), bool):
                    errors.append(f"{result_path}.passed must be boolean")
                matches_expected = (
                    isinstance(result_truth_id, str)
                    and result_truth_id in expected_by_truth_id
                    and _json_equal_strict(
                        result.get("observed"), expected_by_truth_id[result_truth_id]
                    )
                )
                if result.get("passed") is True and not matches_expected:
                    errors.append(f"{result_path}: passed=true requires observed to equal the frozen expected value")
                if result.get("passed") is not True:
                    all_truths_pass = False
                _nonempty_string(result.get("evidence"), f"{result_path}.evidence", errors)
        if _string_set(result_ids) != _string_set(truth_ids) or len(result_ids) != len(truth_ids):
            errors.append(f"{path}: acceptance result truth_id set must exactly match acceptance_truths")

        branches = condition.get("branches")
        branch_ids: list[Any] = []
        all_branches_completed = True
        if not isinstance(branches, list):
            errors.append(f"{path}.branches must be an array")
            branches = []
        for branch_index, raw_branch in enumerate(branches):
            branch_path = f"{path}.branches[{branch_index}]"
            branch = _object(raw_branch, branch_path, {"branch_id", "status", "handling", "artifact_sha256"}, {"branch_id", "status", "handling", "artifact_sha256"}, errors)
            if not branch:
                continue
            branch_ids.append(branch.get("branch_id"))
            _nonempty_string(branch.get("branch_id"), f"{branch_path}.branch_id", errors)
            status = branch.get("status")
            handling = branch.get("handling")
            if status not in ("completed", "missing", "degraded", "blocked"):
                errors.append(f"{branch_path}.status is invalid")
            if handling not in ("included", "fail_closed", "labeled_unknown", "human_review"):
                errors.append(f"{branch_path}.handling is invalid")
            if status != "completed":
                all_branches_completed = False
                if handling not in ("fail_closed", "labeled_unknown", "human_review"):
                    errors.append(f"{branch_path}: missing branch must use fail_closed, labeled_unknown, or human_review")
                if branch.get("artifact_sha256") is not None:
                    errors.append(f"{branch_path}.artifact_sha256 must be null unless completed")
            else:
                _sha256(branch.get("artifact_sha256"), f"{branch_path}.artifact_sha256", errors)
                if handling != "included":
                    errors.append(f"{branch_path}: completed branch handling must be included")
        if _string_set(branch_ids) != set(required_branches) or len(branch_ids) != len(required_branches):
            errors.append(f"{path}: branch_id set must exactly match required_branches")

        costs = _object(condition.get("costs"), f"{path}.costs", {"tool_calls", "latency", "monetary_cost", "merge_repair_actions"}, {"tool_calls", "latency", "monetary_cost", "merge_repair_actions"}, errors)
        if costs:
            for key in ("tool_calls", "merge_repair_actions"):
                if not isinstance(costs.get(key), int) or isinstance(costs.get(key), bool) or costs.get(key, -1) < 0:
                    errors.append(f"{path}.costs.{key} must be a non-negative integer")
            _measurement(costs.get("latency"), f"{path}.costs.latency", errors,
                         allowed_units=("milliseconds",))
            money = _object(costs.get("monetary_cost"), f"{path}.costs.monetary_cost", {"status", "amount", "currency"}, {"status", "amount", "currency"}, errors)
            if money:
                if money.get("status") not in ("measured", "not_available"):
                    errors.append(f"{path}.costs.monetary_cost.status is invalid")
                if money.get("status") == "measured":
                    amount = money.get("amount")
                    if not isinstance(amount, (int, float)) or isinstance(amount, bool) or not math.isfinite(amount) or amount < 0:
                        errors.append(f"{path}.costs.monetary_cost.amount must be finite and non-negative when measured")
                    _nonempty_string(money.get("currency"), f"{path}.costs.monetary_cost.currency", errors)
                elif money.get("amount") is not None or money.get("currency") is not None:
                    errors.append(f"{path}.costs.monetary_cost unavailable values must be null")

        defects = condition.get("hard_gate_defects")
        severe_defect = False
        defect_ids: list[Any] = []
        if not isinstance(defects, list):
            errors.append(f"{path}.hard_gate_defects must be an array")
            defects = []
        for defect_index, raw_defect in enumerate(defects):
            defect_path = f"{path}.hard_gate_defects[{defect_index}]"
            defect = _object(raw_defect, defect_path, {"defect_id", "class", "severity", "description"}, {"defect_id", "class", "severity", "description"}, errors)
            if defect:
                defect_ids.append(defect.get("defect_id"))
                _nonempty_string(defect.get("defect_id"), f"{defect_path}.defect_id", errors)
                if defect.get("class") not in ("authority", "privacy", "fabricated_success", "missing_branch", "source_integrity", "other"):
                    errors.append(f"{defect_path}.class is invalid")
                if defect.get("severity") not in ("severe", "non_severe"):
                    errors.append(f"{defect_path}.severity is invalid")
                severe_defect = severe_defect or defect.get("severity") == "severe"
                _nonempty_string(defect.get("description"), f"{defect_path}.description", errors)
        if _has_duplicate_strings(defect_ids):
            errors.append(f"{path}: hard-gate defect_id values must be unique")

        disposition = _object(condition.get("disposition"), f"{path}.disposition", {"status", "accepted", "reasons"}, {"status", "accepted", "reasons"}, errors)
        if disposition:
            status = disposition.get("status")
            if status not in ("passed", "failed", "blocked", "unresolved"):
                errors.append(f"{path}.disposition.status is invalid")
            if not isinstance(disposition.get("accepted"), bool):
                errors.append(f"{path}.disposition.accepted must be boolean")
            if disposition.get("accepted") is True and status != "passed":
                errors.append(f"{path}.disposition: accepted=true requires status=passed")
            if (status == "passed" or disposition.get("accepted") is True) and capacity_observation_status != "observed":
                errors.append(f"{path}: passed or accepted condition requires capacity_observation_status=observed")
            reasons = _unique_strings(disposition.get("reasons"), f"{path}.disposition.reasons", errors)
            if reasons is not None and not reasons:
                errors.append(f"{path}.disposition.reasons must not be empty")
            if status == "passed":
                if not all_truths_pass:
                    errors.append(f"{path}: passed disposition requires every acceptance truth to pass")
                if not all_branches_completed:
                    errors.append(f"{path}: passed disposition requires every required branch completed")
                if severe_defect:
                    errors.append(f"{path}: passed disposition cannot contain a severe hard-gate defect")
                if not context or context.get("context_fit") is not True:
                    errors.append(f"{path}: passed disposition requires context_fit=true")

    if _string_set(condition_names) != CONDITIONS or len(condition_names) != len(CONDITIONS):
        errors.append("conditions must contain baseline, append_shared, and typed_bounded exactly once")
    if _has_duplicate_strings(condition_ids):
        errors.append("condition_id values must be unique")
    if _has_duplicate_strings(condition_manifest_hashes):
        errors.append("condition_manifest_sha256 values must be unique across conditions")

    final = _object(packet.get("final_disposition"), "$.final_disposition", {"status", "selected_condition", "reasons"}, {"status", "selected_condition", "reasons"}, errors)
    if final:
        status = final.get("status")
        if status not in ("trial_only", "retain_baseline", "blocked", "inconclusive"):
            errors.append("$.final_disposition.status is invalid")
        selected = final.get("selected_condition")
        if selected is not None and (
            not isinstance(selected, str) or selected not in CONDITIONS
        ):
            errors.append("$.final_disposition.selected_condition must name a trial condition or be null")
        reasons = _unique_strings(final.get("reasons"), "$.final_disposition.reasons", errors)
        if reasons is not None and not reasons:
            errors.append("$.final_disposition.reasons must not be empty")

        if status == "retain_baseline" and selected != "baseline":
            errors.append("$.final_disposition: retain_baseline requires selected_condition=baseline")
        if status in ("blocked", "inconclusive", "trial_only") and selected is not None:
            errors.append(f"$.final_disposition: {status} requires selected_condition=null")
        if (
            isinstance(selected, str)
            and selected in condition_by_name
            and condition_by_name[selected].get("disposition", {}).get("accepted") is not True
        ):
            errors.append("selected condition must have disposition.accepted=true")

    limitations = _unique_strings(packet.get("limitations"), "$.limitations", errors)
    if limitations is not None and not limitations:
        errors.append("$.limitations must not be empty")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    args = parser.parse_args(argv)
    boundary = "Structural validation does not prove task truth, source truth, runtime capacity, or orchestration quality."
    try:
        packet = load_packet(args.packet)
        errors = validate_packet(packet)
    except PacketDecodeError as exc:
        print(f"INVALID: {exc}")
        print(boundary)
        return 2
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        print(boundary)
        return 1
    print("VALID")
    print(boundary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
