# Multi-agent context budget and artifact trial

## Experimental instrument status and lifecycle

> **Experimental instrument.** This nested packet and comparison procedure is structurally validated, including hostile fixtures, but no public field evidence is included. It is not a stable parent procedure, a production orchestration standard, or permission to dispatch agents.

Use this reference only when a multi-agent graph is a real candidate and the full-tier triggers in the parent skill apply. It is a capacity preflight and a bounded comparison protocol, not permission to dispatch agents. A fit result says that the intended context path fits the observed runtime under recorded assumptions; it does **not** establish task quality, source truth, privacy, authority, or coordination reliability. Independent shallow bounded fan-out with a simple merge, ample observed margin, and non-consequential missing-branch risk uses the parent's lightweight screen and no packet.

### Lifecycle decisions

- **Promote** the instrument toward stable parent guidance only after fresh representative field packets show a recurring decision or defect-prevention benefit across more than synthetic or authored cases, with acceptable correction burden and no severe authority, privacy, or fabricated-success defect.
- **Revise** it when field use exposes false alarms, missing triggers, validator/schema drift, excess ceremony, misleading measurements, or a cheaper existing evidence path that resolves the same decision.
- **Remove** it when repeated use adds no material decision or repair value, its carrying cost exceeds its benefit, it encourages packet creation for the lightweight tier, or a severe safety, privacy, authority, or false-verification failure makes continued inclusion unjustified.

CI protection while the instrument remains included does not imply permanence. The canaries protect the stated experimental boundary and internal consistency so removal or revision is deliberate; they do not promote the instrument.

## Context-capacity preflight

Complete this before dispatch and again after a material change to the model, runtime, tool payloads, graph, artifact schema, or retrieval policy.

```text
runtime/model identity:
observed usable context limit and observation source:
longest dependency path:
node input artifacts (identity, producer, rendered size):
node output bounds:
duplicated fan-out context:
join inputs and one merge owner:
tool-output reserve:
verification reserve:
expected growth policy:
truncation/compaction behavior:
role-bounded retrieval rule:
missing-branch behavior:
degraded-runtime stop condition:
```

### Preflight procedure

1. Draw the actual dependency graph. Name each node's input artifacts, output artifact and bound, producer, consumers, and local verification. Identify the longest useful serialized path rather than counting agents.
2. Observe the intended provider/model/runtime's usable capacity from the live runtime, a controlled probe, or another recoverable runtime observation. Record the identity, time or version, method, and source. Treat advertised context as an upper bound, not an observed usable limit.
3. Render representative prompts and typed artifacts. Count UTF-8 bytes exactly. Record tokens exactly only when the actual runtime tokenizer measured the rendered input; otherwise use an honest range or `not_measured`. Do not convert bytes to a precise token count with an unexplained ratio.
4. Account separately for prompt/context, duplicated fan-out inputs, join inputs, bounded tool output, and verification reserve. Include compaction summaries only when their production and retrieval path has been tested.
5. Define the expected growth policy. Append-only shared narrative is not the default. Prefer immutable/versioned typed artifacts and retrieval handles restricted to the receiving role's named need.
6. Define branch behavior before dispatch. A required missing, blocked, or degraded branch must fail closed, remain a labeled unknown, or route to human review. It cannot be omitted and then counted as success.
7. Claim `context_fit=true` only when rendered prompt, input artifacts, peak, tool-output reserve, verification reserve, observed limit, declared margin, and runtime capacity are measured in one matching unit. Capacity and context-size measurements accept only `bytes` or `tokens`, including `not_measured` and `context_fit=false` cases; latency accepts only `milliseconds`. For byte/token measurements, exact values and range bounds are non-negative integers; latency milliseconds may be fractional. Validate each measurement's type, unit, method, and bounds before cross-field capacity arithmetic; do not calculate capacity fit across mixed units. The peak lower bound must be at least the rendered-prompt upper bound plus the input-artifact upper bound. The peak upper bound plus both reserve upper bounds must not exceed the observed-limit lower bound, and the declared margin range must match the conservative range derived from those bounds. Stop on runtime degradation that invalidates the observation.
8. Preserve one merge owner and producer/source provenance at the join. Re-run the preflight after any material input or runtime change.

### Dispatch checklist

- [ ] Runtime/model identity and observed usable limit have a recoverable observation source.
- [ ] The longest dependency path, node inputs, output bounds, fan-out duplication, and join inputs are named.
- [ ] Rendered sizes use exact bytes, actual-tokenizer counts, honest ranges, or `not_measured`—never unexplained token precision.
- [ ] Tool-output and verification reserves leave a conservative non-negative margin.
- [ ] Growth, truncation/compaction, and role-bounded retrieval behavior are explicit and tested where relied upon.
- [ ] Every required branch has fail-closed, labeled-unknown, or human-review handling when absent or degraded.
- [ ] One merge owner and producer/source provenance are preserved.
- [ ] The degraded-runtime stop condition and material-change re-preflight trigger are explicit.
- [ ] The graph is still preferable to a single agent after coordination and context costs are counted.

## Linked bounded comparison procedure

The packet and validator exist now; **the orchestration trial has not been run**. Running it requires a separately dispatched, bounded, read-only task. Do not infer a result from the synthetic fixtures.

### Conditions

Freeze immutable task and condition identities before execution. Every condition receives the same source manifest and acceptance truths.

- `baseline`: current parent, independent specialists, and parent merge.
- `append_shared`: each stage receives all prior prose outputs. This is a diagnostic negative control, not the preferred design.
- `typed_bounded`: each stage receives only named typed artifacts and authorized retrieval handles required for its role.

Hash the task manifest, each frozen condition prompt, each complete rendered condition/input contract, and completed branch artifacts with SHA-256. Record the complete contract digest as required `condition_manifest_sha256`; all three values must be distinct. This digest binds the rendered prompt, source/input manifest, acceptance truths, condition contract, and other frozen inputs for that run. The validator only checks digest shape and cross-condition uniqueness—it does not recompute or prove the binding. A rerendered prompt, changed source manifest, changed acceptance truth, or changed condition contract is a new identity, not an in-place correction.

### Task family and cases

Use one non-sensitive, read-only source or artifact review family with real evidence partitions, a merger that must preserve early constraints, deterministic acceptance/source checks, and no external effect. Debug only the harness on a small development set; freeze prompts before a fresh held-out set.

Include at least:

- one long-source case;
- one contradictory-source case;
- one missing-branch case;
- one poisoned or false upstream claim;
- one case where one agent is sufficient and multi-agent overhead should lose.

Do not use finance, health, household, client, messaging, credential-bearing, or mutation tasks. Do not claim statistical generalization from this bounded comparison.

### Equalization and observations

Hold source materials, task manifest, acceptance truths, model/provider where feasible, tool access, and matched call/time budget constant. Record deviations as limitations rather than silently normalizing them away.

For each condition record:

- observed provider/model/runtime and usable capacity with source;
- rendered prompt and artifact measurements, peak context, observed limit, and margin;
- every acceptance truth and its condition-specific observation/evidence;
- every required branch and explicit handling of missing/degraded/blocked states;
- tool calls, latency, monetary cost when available, and merge repair actions;
- authority, privacy, fabricated-success, missing-branch, or source-integrity hard-gate defects;
- condition disposition and final trial disposition.

### Validator authority

The Python validator at `scripts/validate_context_trial_packet.py` is the normative executable authority. The JSON Schema at `references/context-trial-packet-v1.schema.json` is an informative interoperability representation. Drift between them blocks release; update and test both, but resolve semantic uncertainty in favor of the Python validator until an explicit versioned contract change is reviewed.

The validator rejects duplicate JSON keys, non-finite numbers, fractional exact or ranged byte/token counts, unknown fields, malformed or duplicate condition identities, impossible passed states, silently missing branches, and unreconciled context-fit claims. Acceptance `expected` and `observed` values use recursive strict JSON type/value equality, so booleans never compare equal to numbers, including inside arrays or objects. Final dispositions are closed: `retain_baseline` selects an accepted `baseline`; `trial_only`, `blocked`, and `inconclusive` select `null`; v1 has no promotion status. The validator deliberately performs no network lookup, runtime probe, digest recomputation, trial execution, or truth adjudication.

### Separate aggregation and adoption decision

The single-case v1 packet cannot encode a machine-valid promotion. Aggregate results across fresh held-out packets separately, then make a human-reviewed adoption decision only if the evidence shows all of the following:

- zero severe authority, privacy, or fabricated-success defects;
- at least two recurring defects caught that baseline misses, or a material reduction in correction burden;
- acceptance truth preserved or improved;
- median time/tool/context cost no more than roughly 25% above baseline unless the extra cost prevents a consequential defect;
- the procedure remains understandable and removable.

`append_shared` remains diagnostic unless it unexpectedly wins under the same hard gates. One synthetic fixture, one development case, context fit, or validator success cannot promote a condition; the synthetic fixture can only remain trial-only evidence of representation behavior.

## Packet commands

Run the packet tools from either of these explicit roots. An absolute repository root may point to a private checkout; it does not need to be public or use a particular parent directory.

Installed skill root:

```bash
SKILL_ROOT="${HOME}/.hermes/skills/agent-ops/agent-prompt-design"
python3 "${SKILL_ROOT}/scripts/test_context_trial_packet.py"
python3 "${SKILL_ROOT}/scripts/validate_context_trial_packet.py" \
  "${SKILL_ROOT}/references/examples/context-trial-valid-synthetic.json"
python3 -m py_compile \
  "${SKILL_ROOT}/scripts/validate_context_trial_packet.py" \
  "${SKILL_ROOT}/scripts/test_context_trial_packet.py"
```

Repository root (set `REPO_ROOT` to the absolute path of the checkout, including a private checkout):

```bash
REPO_ROOT="/absolute/path/to/herbert"
SKILL_ROOT="${REPO_ROOT}/skills/agent-prompt-design"
python3 "${SKILL_ROOT}/scripts/test_context_trial_packet.py"
python3 "${SKILL_ROOT}/scripts/validate_context_trial_packet.py" \
  "${SKILL_ROOT}/references/examples/context-trial-valid-synthetic.json"
python3 -m py_compile \
  "${SKILL_ROOT}/scripts/validate_context_trial_packet.py" \
  "${SKILL_ROOT}/scripts/test_context_trial_packet.py"
```

The valid example is labeled synthetic and exists only to exercise the representation. The duplicate-key example is intentionally invalid. Neither is trial evidence.
