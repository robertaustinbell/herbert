---
name: authority-effect-contracts
description: Use for subagent manifests and external-effect receipts.
license: MIT
metadata:
  version: 0.1.0
  author: Bobert
  hermes:
    tags: [authority, receipts, delegation, validation, provenance]
    related_skills: [agent-prompt-design, deterministic-evidence-automation, agent-provenance-observability]
---

# Authority and Effect Contracts

## Purpose

Generate and deterministically validate two versioned contracts:

- `authority-manifest/v1` makes a consequential delegation envelope inspectable and supports parent-to-child non-escalation checks.
- `external-effect-receipt/v1` keeps request, preparation, attempt, observation, and evidence completeness distinct.

Operating thought remains the semantic owner. This skill validates representation and subset rules; it is not a security sandbox and does not itself grant authority or prove that an external effect occurred.

## When to Use

Use only when a consequential delegated or automated task benefits from machine-checkable scope or when an external-effect success claim needs a structured receipt. Skip for routine read-only lookup and already-authorized mechanical work where the contract cannot alter execution, review, or repair.

1. Start from the examples under `references/examples/`.
2. Validate manifests with `scripts/validate_authority_manifest.py`.
3. Before dispatch, validate the child against its parent with `scripts/check_authority_subset.py`.
4. Validate effect receipts with `scripts/validate_effect_receipt.py`.
5. Treat a valid receipt as a structurally conforming claim. Independently verify its handle or read-back when consequential.
6. Revalidate when task, target, executor, policy, requested effect, or contract version changes.

Use the shared [Composition contract](../COMPOSITION.md) for artifact ownership, lifecycle order, task/run correlation, downstream handle resolution, staleness, and failure behavior. These validators own only their stated structural checks.

## Commands

```bash
python3 scripts/validate_authority_manifest.py manifest.json
python3 scripts/check_authority_subset.py parent.json child.json
python3 scripts/validate_effect_receipt.py receipt.json
python3 scripts/test_contracts.py
```

Each validator emits JSON and exits `0` on acceptance or `1` on contract failure. CLI misuse exits `2`.

## Contract boundaries

- Unknown fields fail closed.
- Duplicate JSON keys are rejected by the provided CLIs before validation, including nested objects and both subset-check inputs. Direct Python callers must use an equivalently strict parser; normal `json.loads` alone silently keeps one duplicate value.
- Parent and child must share the same `task_id`; prose may narrow the task but cannot silently rebind it to a different delegation.
- Child `may` actions and exact-string targets must be subsets of the parent; this does not resolve paths, aliases, symlinks, or semantic resource identity.
- **Path-semantics pitfall:** target subset checks compare strings only. For example, `./output` and `/project/output` may resolve to the same location while validation treats them as unrelated targets; a passing subset check is not proof of distinct or semantically narrowed resources.
- Child prohibitions, approval gates, verification obligations, and stop conditions must preserve or strengthen the parent.
- Child validity cannot outlive the parent, and dispatch-oriented CLI validation rejects expired manifests.
- Validate enum types before membership checks: `effect_status`, `evidence_completeness`, and evidence kinds must be strings from their declared vocabularies. Malformed values produce contract diagnostics, not Python type errors.
- `partial` belongs to `evidence_completeness`, never `effect_status`.
- `observed_succeeded` requires acting-surface metadata and a recognized evidence class with non-empty handle and observed result. The validator does not resolve the handle or prove the result.
- Future-dated effect observations beyond five minutes of clock skew are rejected.
- Requested, prepared, attempted, and unknown states are not success.
- Declared sensitive payload retention is rejected; callers must still sanitize bounded metadata and evidence values because structural validation is not secret detection.

## Worked example

The fixture suite performs a real reversible local write into a temporary directory, hashes the report, creates an `observed_succeeded` receipt, validates it, and removes the directory. The static success example is only a structurally valid illustration; it is not proof that its example effect occurred. Invalid fixtures and unit tests cover action and target escalation, task rebinding, expiry, future observations, dropped requirements, unknown evidence classes, false success without evidence, state-vocabulary confusion, unknown fields, and declared sensitive-payload retention.

## Verification and status

This is a bounded executable spike and an inspectable checklist, not an authority boundary. Its first representative read-only delegation produced modest review clarity but no demonstrated runtime control effect: the manifest made limits auditable yet remained redundant with explicit instructions and was not enforced by the tool runtime. Passing fixtures validate the current schema and validator behavior, not Hermes runtime enforcement or production utility. Do not integrate universally until representative use shows that the fields change review or prevent scope/error ambiguity without disproportionate ceremony.

Schemas provide portable structural contracts. The Python validators are the executable semantic authority for cross-field rules, parent-child subset checks, and state-specific receipt evidence that JSON Schema alone does not fully express.

Schemas:

- `references/schemas/authority-manifest-v1.schema.json`
- `references/schemas/external-effect-receipt-v1.schema.json`

Examples:

- `references/examples/authority-parent-valid.json`
- `references/examples/authority-child-valid.json`
- `references/examples/authority-child-escalation-invalid.json`
- `references/examples/receipt-requested-valid.json`
- `references/examples/receipt-success-valid.json`
- `references/examples/receipt-success-without-evidence-invalid.json`
