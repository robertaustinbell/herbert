#!/usr/bin/env python3
"""Tests for the context trial packet validator."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
FIXTURES = SKILL_ROOT / "references" / "examples"
SCHEMA = SKILL_ROOT / "references" / "context-trial-packet-v1.schema.json"
VALIDATOR = HERE / "validate_context_trial_packet.py"
sys.path.insert(0, str(HERE))

from validate_context_trial_packet import PacketDecodeError, load_packet, validate_packet  # noqa: E402


class ContextTrialPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.synthetic = load_packet(FIXTURES / "context-trial-valid-synthetic.json")
        cls.valid = copy.deepcopy(cls.synthetic)
        for condition in cls.valid["conditions"]:
            condition["runtime"]["capacity_observation_status"] = "observed"
            condition["context"]["context_fit"] = True
            for result in condition["acceptance_results"]:
                result["passed"] = True
            condition["disposition"]["status"] = "passed"

    def errors_after(self, mutate):
        packet = copy.deepcopy(self.valid)
        mutate(packet)
        return validate_packet(packet)

    def assertRejected(self, mutate, fragment):
        errors = self.errors_after(mutate)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_capacity_measurements_reject_time_units_even_without_fit(self):
        fields = [("runtime", "observed_usable_capacity")] + [
            ("context", key) for key in (
                "rendered_prompt", "input_artifacts", "tool_output_reserve",
                "verification_reserve", "peak_rendered_context", "observed_limit", "margin",
            )
        ]
        for section, field in fields:
            for kind in ("exact", "range", "not_measured"):
                for fit in (False, True):
                    with self.subTest(section=section, field=field, kind=kind, fit=fit):
                        packet = copy.deepcopy(self.valid)
                        condition = packet["conditions"][0]
                        condition["context"]["context_fit"] = fit
                        measurement = {"kind": kind, "unit": "milliseconds", "method": "clock"}
                        if kind == "exact":
                            measurement["value"] = 1
                        elif kind == "range":
                            measurement.update(lower=1, upper=2)
                        condition[section][field] = measurement
                        errors = validate_packet(packet)
                        self.assertTrue(any(
                            f"{section}.{field}.unit must be bytes or tokens" in error
                            for error in errors
                        ), errors)

    def test_latency_rejects_capacity_units_for_all_measurement_kinds(self):
        for kind in ("exact", "range", "not_measured"):
            for unit, method in (("bytes", "utf8_byte_count"), ("tokens", "runtime_tokenizer")):
                with self.subTest(kind=kind, unit=unit):
                    packet = copy.deepcopy(self.valid)
                    measurement = {"kind": kind, "unit": unit, "method": method}
                    if kind == "exact":
                        measurement["value"] = 1
                    elif kind == "range":
                        measurement.update(lower=1, upper=2)
                    packet["conditions"][0]["costs"]["latency"] = measurement
                    self.assertTrue(any(
                        "costs.latency.unit must be milliseconds" in error
                        for error in validate_packet(packet)
                    ))

    def test_consistent_capacity_units_and_latency_remain_valid(self):
        for unit, method in (("bytes", "utf8_byte_count"), ("tokens", "runtime_tokenizer")):
            with self.subTest(unit=unit):
                packet = copy.deepcopy(self.valid)
                for condition in packet["conditions"]:
                    measurements = [condition["runtime"]["observed_usable_capacity"]] + [
                        value for value in condition["context"].values() if isinstance(value, dict)
                    ]
                    for measurement in measurements:
                        measurement["unit"] = unit
                        if measurement["kind"] == "exact":
                            measurement["method"] = method
                self.assertEqual([], validate_packet(packet))

    def test_time_units_cannot_pass_context_fit_cli(self):
        packet = copy.deepcopy(self.valid)
        for condition in packet["conditions"]:
            measurements = [condition["runtime"]["observed_usable_capacity"]] + [
                value for value in condition["context"].values() if isinstance(value, dict)
            ]
            for measurement in measurements:
                measurement["unit"] = "milliseconds"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "packet.json"
            path.write_text(json.dumps(packet), encoding="utf-8")
            result = subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn(".unit must be bytes or tokens", result.stdout)

    def test_invalid_or_mixed_measurements_are_not_used_in_capacity_math(self):
        for update in (
            {"unit": "milliseconds", "lower": 999999, "upper": 999999},
            {"unit": "bytes", "lower": 999999, "upper": 999999},
            {"lower": -2, "upper": -1},
            {"lower": 999999, "upper": 1},
            {"unit": []},
            {"method": None},
        ):
            with self.subTest(update=update):
                packet = copy.deepcopy(self.valid)
                packet["conditions"][0]["context"]["peak_rendered_context"].update(update)
                errors = validate_packet(packet)
                self.assertTrue(errors)
                for fragment in (
                    "peak lower bound must cover", "peak plus reserves exceeds",
                    "declared margin bounds must match",
                ):
                    self.assertFalse(any(fragment in error for error in errors), errors)

    def test_schema_limits_units_by_measurement_role(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        definitions = schema["$defs"]
        capacity = [definitions["runtime"]["properties"]["observed_usable_capacity"]] + [
            value for value in definitions["context"]["properties"].values()
            if value.get("$ref") == "#/$defs/measurement"
        ]
        self.assertEqual(len(capacity), 8)
        for measurement in capacity:
            self.assertEqual(
                measurement.get("properties", {}).get("unit", {}).get("enum"),
                ["bytes", "tokens"],
            )
        latency = definitions["costs"]["properties"]["latency"]
        self.assertEqual(latency.get("properties", {}).get("unit", {}).get("enum"), ["milliseconds"])

    def test_valid_synthetic_packet_passes(self):
        self.assertEqual([], validate_packet(copy.deepcopy(self.synthetic)))

    def test_cli_rejects_nested_duplicate_keys_before_contract_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "packet.json"
            path.write_text('{"conditions": [{"context": {"unit": "bytes", "unit": "tokens"}}]}', encoding="utf-8")
            result = subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("INVALID: duplicate key: unit", result.stdout)

    def test_duplicate_json_keys_fail_closed(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            handle.write('{"schema_version":"context-trial-packet/v1","schema_version":"context-trial-packet/v1"}')
            path = Path(handle.name)
        self.addCleanup(path.unlink)
        with self.assertRaisesRegex(PacketDecodeError, "duplicate key"):
            load_packet(path)

    def test_unknown_fields_fail_closed_at_nested_levels(self):
        self.assertRejected(lambda p: p["conditions"][0]["runtime"].update({"surprise": True}), "unknown field")

    def test_condition_set_and_immutable_ids_are_exact_and_unique(self):
        self.assertRejected(lambda p: p["conditions"][2].update({"condition": "baseline"}), "conditions must contain")
        self.assertRejected(lambda p: p["conditions"][2].update({"condition_id": p["conditions"][0]["condition_id"]}), "condition_id values must be unique")

    def test_identity_hashes_are_required_and_sha256_shaped(self):
        self.assertRejected(lambda p: p["task"].update({"task_manifest_sha256": "mutable"}), "task_manifest_sha256")
        self.assertRejected(lambda p: p["conditions"][0].update({"prompt_sha256": "mutable"}), "prompt_sha256")

    def test_condition_manifest_hash_is_required_for_every_condition(self):
        self.assertRejected(
            lambda p: p["conditions"][0].pop("condition_manifest_sha256"),
            "missing required field condition_manifest_sha256",
        )

    def test_condition_manifest_hashes_must_be_distinct_across_conditions(self):
        self.assertRejected(
            lambda p: p["conditions"][1].update({
                "condition_manifest_sha256": p["conditions"][0]["condition_manifest_sha256"]
            }),
            "condition_manifest_sha256 values must be unique across conditions",
        )

    def test_malformed_identity_types_return_errors_instead_of_crashing(self):
        self.assertRejected(lambda p: p["conditions"][0].update({"condition_id": {"mutable": True}}), "condition_id must be a non-empty string")

    def test_object_valued_measurement_kind_fails_closed(self):
        self.assertRejected(
            lambda p: p["conditions"][0]["context"]["rendered_prompt"].update(
                {"kind": {"confused": True}}
            ),
            "rendered_prompt.kind must be exact, range, or not_measured",
        )

    def test_object_valued_measurement_unit_fails_closed(self):
        self.assertRejected(
            lambda p: p["conditions"][0]["context"]["rendered_prompt"].update(
                {"unit": {"confused": True}}
            ),
            "rendered_prompt.unit must be bytes or tokens",
        )

    def test_exact_token_measurement_requires_runtime_tokenizer(self):
        def mutate(packet):
            packet["conditions"][0]["context"]["peak_rendered_context"] = {
                "kind": "exact", "unit": "tokens", "value": 21001, "method": "estimate"
            }
        self.assertRejected(mutate, "exact token measurements require method runtime_tokenizer")

    def test_nonstandard_numeric_constants_fail_at_json_load(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
                    handle.write('{"value":' + constant + '}')
                    path = Path(handle.name)
                self.addCleanup(path.unlink)
                with self.assertRaisesRegex(PacketDecodeError, "invalid JSON constant"):
                    load_packet(path)

    def test_nonfinite_numbers_fail_numeric_validation(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                self.assertRejected(
                    lambda p, value=value: p["conditions"][0]["costs"]["latency"].update(
                        {"kind": "exact", "value": value}
                    ),
                    "must be a finite non-negative number",
                )

    def test_exact_token_and_byte_counts_require_integers(self):
        for key, unit, method in (
            ("peak_rendered_context", "tokens", "runtime_tokenizer"),
            ("rendered_prompt", "bytes", "utf8_byte_count"),
        ):
            with self.subTest(unit=unit):
                self.assertRejected(
                    lambda p, key=key, unit=unit, method=method: p["conditions"][0]["context"].update(
                        {key: {"kind": "exact", "unit": unit, "value": 1.5, "method": method}}
                    ),
                    "exact bytes/tokens must be a non-negative integer",
                )

    def test_exact_milliseconds_may_be_fractional(self):
        packet = copy.deepcopy(self.valid)
        packet["conditions"][0]["costs"]["latency"] = {
            "kind": "exact", "unit": "milliseconds", "value": 1.5, "method": "monotonic_clock"
        }
        self.assertEqual([], validate_packet(packet))

    def test_range_token_and_byte_counts_require_integer_bounds(self):
        for unit, key in (("tokens", "peak_rendered_context"), ("bytes", "rendered_prompt")):
            with self.subTest(unit=unit):
                def mutate(packet, unit=unit, key=key):
                    measurement = packet["conditions"][0]["context"][key]
                    measurement.update({"kind": "range", "unit": unit, "lower": 1.5, "upper": 2.5})
                    measurement.pop("value", None)
                self.assertRejected(mutate, "range bytes/tokens bounds must be non-negative integers")

    def test_range_milliseconds_may_be_fractional(self):
        packet = copy.deepcopy(self.valid)
        packet["conditions"][0]["costs"]["latency"] = {
            "kind": "range", "unit": "milliseconds", "lower": 1.5, "upper": 2.5,
            "method": "monotonic_clock"
        }
        self.assertEqual([], validate_packet(packet))

    def test_range_measurements_require_ordered_bounds(self):
        self.assertRejected(
            lambda p: p["conditions"][0]["context"]["margin"].update({"lower": 90000, "upper": 80000}),
            "lower must not exceed upper",
        )

    def test_context_fit_requires_observed_limit_and_margin(self):
        self.assertRejected(lambda p: p["conditions"][0]["context"].pop("observed_limit"), "context_fit=true requires observed_limit")
        self.assertRejected(lambda p: p["conditions"][0]["context"].pop("margin"), "context_fit=true requires margin")

    def test_runtime_requires_explicit_capacity_observation_status(self):
        self.assertRejected(
            lambda p: p["conditions"][0]["runtime"].pop("capacity_observation_status", None),
            "missing required field capacity_observation_status",
        )
        self.assertRejected(
            lambda p: p["conditions"][0]["runtime"].update({"capacity_observation_status": "guessed"}),
            "capacity_observation_status must be observed or not_observed",
        )

    def test_object_valued_capacity_observation_status_fails_closed(self):
        self.assertRejected(
            lambda p: p["conditions"][0]["runtime"].update(
                {"capacity_observation_status": {"confused": True}}
            ),
            "capacity_observation_status must be observed or not_observed",
        )

    def test_declared_guess_cannot_claim_context_fit(self):
        def mutate(packet):
            runtime = packet["conditions"][0]["runtime"]
            runtime["capacity_observation_status"] = "not_observed"
            runtime["capacity_source"] = "declared guess presented as an observed runtime probe"
            runtime["observed_usable_capacity"]["source"] = "synthetic source claiming observed fit"

        self.assertRejected(mutate, "context_fit=true requires capacity_observation_status=observed")

    def test_passed_or_accepted_condition_requires_observed_capacity(self):
        for disposition in (
            {"status": "passed", "accepted": False},
            {"status": "passed", "accepted": True},
        ):
            with self.subTest(disposition=disposition):
                def mutate(packet, disposition=disposition):
                    runtime = packet["conditions"][0]["runtime"]
                    runtime["capacity_observation_status"] = "not_observed"
                    packet["conditions"][0]["context"]["context_fit"] = False
                    packet["conditions"][0]["disposition"].update(disposition)
                self.assertRejected(mutate, "passed or accepted condition requires capacity_observation_status=observed")

    def test_context_fit_requires_all_capacity_measurements_to_be_measured(self):
        for key in ("peak_rendered_context", "tool_output_reserve", "verification_reserve", "observed_limit", "margin"):
            with self.subTest(key=key):
                def mutate(packet, key=key):
                    measurement = packet["conditions"][0]["context"][key]
                    packet["conditions"][0]["context"][key] = {
                        "kind": "not_measured", "unit": measurement["unit"], "method": "not_measured"
                    }
                self.assertRejected(mutate, f"context_fit=true requires measured {key}")

    def test_context_fit_requires_matching_capacity_units(self):
        def mutate(packet):
            context = packet["conditions"][0]["context"]
            context["rendered_prompt"] = {
                "kind": "exact", "unit": "bytes", "value": 12000, "method": "utf8_byte_count"
            }
            context["input_artifacts"] = {
                "kind": "exact", "unit": "tokens", "value": 20000, "method": "runtime_tokenizer"
            }
        self.assertRejected(mutate, "context-fit measurements must use the same unit")

    def test_runtime_capacity_unit_and_bounds_must_match_observed_limit(self):
        def mismatched_unit(packet):
            packet["conditions"][0]["runtime"]["observed_usable_capacity"]["unit"] = "bytes"
        self.assertRejected(mismatched_unit, "observed_limit must match runtime observed_usable_capacity units and bounds")

        def mismatched_bounds(packet):
            packet["conditions"][0]["runtime"]["observed_usable_capacity"]["lower"] = 91000
        self.assertRejected(mismatched_bounds, "observed_limit must match runtime observed_usable_capacity units and bounds")

    def test_context_fit_rejects_impossible_conservative_arithmetic(self):
        def mutate(packet):
            context = packet["conditions"][0]["context"]
            context["peak_rendered_context"].update({"lower": 80000, "upper": 80000})
        self.assertRejected(mutate, "peak plus reserves exceeds the conservative observed limit")

    def test_context_fit_rejects_peak_smaller_than_rendered_components(self):
        def mutate(packet):
            context = packet["conditions"][0]["context"]
            context["peak_rendered_context"].update({"lower": 30000, "upper": 36000})
            context["margin"].update({"lower": 30000, "upper": 54000})
        self.assertRejected(mutate, "peak lower bound must cover rendered prompt and input artifact upper bounds")

    def test_declared_margin_must_match_derived_capacity_range(self):
        def mutate(packet):
            packet["conditions"][0]["context"]["margin"].update({"lower": 0, "upper": 1})
        self.assertRejected(mutate, "declared margin bounds must match the derived capacity range")

    def test_acceptance_truth_ids_must_match_exactly(self):
        self.assertRejected(lambda p: p["conditions"][0]["acceptance_results"].clear(), "acceptance result truth_id set must exactly match")

    def test_object_valued_hard_gate_defect_class_fails_closed(self):
        def mutate(packet):
            packet["conditions"][0]["hard_gate_defects"].append({
                "defect_id": "type-confused-class",
                "class": {"confused": True},
                "severity": "non_severe",
                "description": "synthetic type-confusion probe",
            })

        self.assertRejected(mutate, ".hard_gate_defects[0].class is invalid")

    def test_object_valued_hard_gate_defect_severity_fails_closed(self):
        def mutate(packet):
            packet["conditions"][0]["hard_gate_defects"].append({
                "defect_id": "type-confused-severity",
                "class": "other",
                "severity": {"confused": True},
                "description": "synthetic type-confusion probe",
            })

        self.assertRejected(mutate, ".hard_gate_defects[0].severity is invalid")

    def test_impossible_passed_state_is_rejected(self):
        def failed_truth(packet):
            packet["conditions"][0]["acceptance_results"][0]["passed"] = False
        self.assertRejected(failed_truth, "passed disposition requires every acceptance truth to pass")

        def hard_gate(packet):
            packet["conditions"][0]["hard_gate_defects"].append({
                "defect_id": "defect-1", "class": "fabricated_success", "severity": "severe", "description": "synthetic"
            })
        self.assertRejected(hard_gate, "passed disposition cannot contain a severe hard-gate defect")

    def test_passed_truth_must_match_frozen_expected_value(self):
        def mutate(packet):
            packet["conditions"][0]["acceptance_results"][0].update({"observed": False, "passed": True})
        self.assertRejected(mutate, "passed=true requires observed to equal the frozen expected value")

    def test_acceptance_comparison_uses_strict_recursive_json_types(self):
        def mutate(packet):
            packet["acceptance_truths"][0]["expected"] = {"nested": [1]}
            for condition in packet["conditions"]:
                condition["acceptance_results"][0].update({
                    "observed": {"nested": [True]}, "passed": True
                })
        self.assertRejected(mutate, "passed=true requires observed to equal the frozen expected value")

    def test_object_valued_condition_disposition_status_fails_closed(self):
        self.assertRejected(
            lambda p: p["conditions"][0]["disposition"].update(
                {"status": {"confused": True}}
            ),
            ".disposition.status is invalid",
        )

    def test_accepted_condition_must_have_passed_disposition(self):
        def mutate(packet):
            packet["conditions"][0]["disposition"].update({"status": "failed", "accepted": True})
        self.assertRejected(mutate, "accepted=true requires status=passed")

    def test_object_valued_branch_status_fails_closed(self):
        self.assertRejected(
            lambda p: p["conditions"][0]["branches"][0].update(
                {"status": {"confused": True}}
            ),
            ".branches[0].status is invalid",
        )

    def test_object_valued_branch_handling_fails_closed(self):
        self.assertRejected(
            lambda p: p["conditions"][0]["branches"][0].update(
                {"handling": {"confused": True}}
            ),
            ".branches[0].handling is invalid",
        )

    def test_missing_branch_cannot_be_silent_success(self):
        def mutate(packet):
            packet["conditions"][0]["branches"][0].update({"status": "missing", "handling": "included", "artifact_sha256": None})
        self.assertRejected(mutate, "missing branch must use fail_closed, labeled_unknown, or human_review")
        self.assertRejected(mutate, "passed disposition requires every required branch completed")

    def test_object_valued_monetary_cost_status_fails_closed(self):
        self.assertRejected(
            lambda p: p["conditions"][0]["costs"]["monetary_cost"].update(
                {"status": {"confused": True}}
            ),
            ".costs.monetary_cost.status is invalid",
        )

    def test_costs_and_final_disposition_are_required(self):
        self.assertRejected(lambda p: p["conditions"][0].pop("costs"), "missing required field costs")
        self.assertRejected(lambda p: p.pop("final_disposition"), "missing required field final_disposition")

    def test_object_valued_final_disposition_status_fails_closed(self):
        self.assertRejected(
            lambda p: p["final_disposition"].update(
                {"status": {"confused": True}}
            ),
            "$.final_disposition.status is invalid",
        )

    def test_single_case_packet_cannot_encode_machine_valid_promotion(self):
        def mutate(packet):
            packet["final_disposition"].update({
                "status": "promote_typed_bounded", "selected_condition": "typed_bounded"
            })
        self.assertRejected(mutate, "$.final_disposition.status is invalid")

    def test_object_valued_selected_condition_fails_closed(self):
        self.assertRejected(
            lambda p: p["final_disposition"].update(
                {"selected_condition": {"confused": True}}
            ),
            "$.final_disposition.selected_condition must name a trial condition or be null",
        )

    def test_trial_only_disposition_cannot_select_a_condition(self):
        self.assertRejected(
            lambda p: p["final_disposition"].update({"selected_condition": "typed_bounded"}),
            "trial_only requires selected_condition=null",
        )

    def test_contradictory_final_dispositions_are_rejected(self):
        for status, selected, fragment in (
            ("blocked", "baseline", "blocked requires selected_condition=null"),
            ("inconclusive", "baseline", "inconclusive requires selected_condition=null"),
            ("retain_baseline", None, "retain_baseline requires selected_condition=baseline"),
            ("retain_baseline", "typed_bounded", "retain_baseline requires selected_condition=baseline"),
        ):
            with self.subTest(status=status, selected=selected):
                self.assertRejected(
                    lambda p, status=status, selected=selected: p["final_disposition"].update({
                        "status": status, "selected_condition": selected
                    }),
                    fragment,
                )

    def test_schema_removes_machine_valid_promotion_status(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("Informative interoperability representation", schema["description"])
        self.assertIn("Python validator is normative executable authority", schema["description"])
        self.assertIn("drift blocks release", schema["description"])
        statuses = schema["$defs"]["final_disposition"]["properties"]["status"]["enum"]
        self.assertNotIn("promote_typed_bounded", statuses)

    def test_schema_requires_condition_manifest_and_integer_byte_token_ranges(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        condition = schema["$defs"]["condition_run"]
        self.assertIn("condition_manifest_sha256", condition["required"])
        self.assertEqual(
            "#/$defs/sha256",
            condition["properties"]["condition_manifest_sha256"]["$ref"],
        )
        range_measurement = schema["$defs"]["measurement"]["oneOf"][1]
        self.assertTrue(any(
            rule.get("then", {}).get("properties", {}).get("lower", {}).get("type") == "integer"
            for rule in range_measurement.get("allOf", [])
        ))

    def test_schema_requires_explicit_capacity_observation_status(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        runtime = schema["$defs"]["runtime"]
        self.assertIn("capacity_observation_status", runtime["required"])
        self.assertEqual(
            ["observed", "not_observed"],
            runtime["properties"]["capacity_observation_status"]["enum"],
        )
        condition_run = schema["$defs"]["condition_run"]
        self.assertIn("allOf", condition_run)
        condition_rules = condition_run["allOf"]
        fit_rule = next(
            rule for rule in condition_rules
            if rule.get("if", {}).get("properties", {}).get("context")
        )
        self.assertEqual(
            "observed",
            fit_rule["then"]["properties"]["runtime"]["properties"]["capacity_observation_status"]["const"],
        )
        disposition_rule = next(
            rule for rule in condition_rules
            if rule.get("if", {}).get("properties", {}).get("disposition")
        )
        self.assertEqual(
            "observed",
            disposition_rule["then"]["properties"]["runtime"]["properties"]["capacity_observation_status"]["const"],
        )

    def test_cli_reports_boundary_and_exit_status(self):
        valid = subprocess.run([sys.executable, str(VALIDATOR), str(FIXTURES / "context-trial-valid-synthetic.json")], text=True, capture_output=True)
        self.assertEqual(0, valid.returncode, valid.stderr)
        self.assertIn("does not prove task truth", valid.stdout)

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            handle.write("{")
            malformed = Path(handle.name)
        self.addCleanup(malformed.unlink)
        invalid = subprocess.run([sys.executable, str(VALIDATOR), str(malformed)], text=True, capture_output=True)
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn("INVALID", invalid.stdout)


if __name__ == "__main__":
    unittest.main()
