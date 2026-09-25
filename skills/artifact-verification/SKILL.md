---
name: artifact-verification
description: "Use when fresh verification is needed for local artifacts."
version: 1.3.1
author: Bobert
license: MIT
metadata:
  hermes:
    tags: [verification, artifacts, evidence, smoke-testing, local]
    related_skills: [safe-code-change, deterministic-evidence-automation]
---

# Artifact Verification

Use this class-level procedure when a codebase, static site, generated bundle, document, or other local artifact needs fresh evidence of a changed contract and the available test evidence is stale, incomplete, or not canonical.

The goal is not to manufacture a green status. The goal is to produce a small, inspectable evidence packet tied to the current workspace, with failures separated into implementation failures, harness failures, environment failures, and scope gaps.

## Triggers

- The workspace reports `unverified`, stale, or missing verification evidence.
- A requested change has no canonical automated suite.
- A build or generated artifact must be checked against the current source.
- A local web artifact needs a representative HTTP smoke test.
- Historical command output exists but the current changed paths have not been exercised together.

Do not use this as a substitute for a project’s canonical tests when those tests exist and are applicable. Use the project’s documented verification first or in addition, proportionate to blast radius.

## Procedure

1. **State acceptance truths before choosing checks.** Name the smallest observable truths that must hold for the requested result to be correct. Each mandatory truth is its own metric: do not blend unrelated checks into one quality score. Name the metric in the same words as the truth. Work backward from each truth to the required artifact, wiring, behavior, and observer. Keep the evidence ladder explicit: `requested` → `attempted` → `acting surface acknowledged` → `independently observed effect` → `user-visible or consumer-usable outcome`. Do not report a higher state than the strongest one directly established; tool acceptance, process launch, file existence, and adapter success are not user-visible success. Treat implementation notes, executor summaries, subagent reports, and prior test output as claims to verify—not proof. Treat human or model "looks good" and blended scores the same way. For a canary or comparative trial, freeze 3–8 authored cases and expected terminal states before reviewing outputs.
2. **Scope and fingerprint the current state.** Inspect the current status/diff and identify the changed contract, generated outputs, and any sensitive paths that must not be read or emitted. Capture the narrowest stable source identity available—such as commit, changed-path set, content hash, or explicit dirty-state description—so the result cannot silently certify a later state. If the source changes after verification, mark the receipt stale and rerun the affected checks.
3. **Map truths to direct checks from observed contracts.** For every acceptance truth, identify the artifact and behavior that would establish it, then record `verified`, `failed`, `blocked`, or `unresolved`. If the truth is mechanical (HTTP status, body bytes, header, file hash, test name, exact string), own the verdict with a code or regex assertion. Use model judgment only for claims that cannot be observed. When both exist, the code check owns the metric. Assert the behavior that changed, not merely the existence of files. Before writing assertions, inspect the current artifact, schema, headings, test names, and result keys; copy exact identifiers from evidence instead of guessing them from memory or a summary. For HTML/CSS, check semantic markers, accessibility attributes, expected counts, asset references, and relevant responsive/reduced-motion rules. For other artifacts, define the smallest observable contract.
4. **Use the simplest sufficient verification path.** Run applicable canonical checks directly. Add an isolated verifier only for acceptance truths those checks do not establish, using an approved temporary workspace outside the delivered artifact. Invoke it through the runtime's documented evidence-capture path, verify that the record binds the actual execution to the current artifact, and clean up afterward. Temporary-directory choice, filename prefixes, and invocation constraints belong to the applicable runtime adapter; they are not universal verification requirements. See the conditional adapter in `references/fresh-local-verification.md`.
5. **Exercise the build boundary.** Run the project’s build or generation command when it is part of the artifact path. Check both the exit code and the generated files that matter; do not infer generated correctness from a successful source-only check.
6. **Smoke-test realistic outputs.** For local web artifacts, serve the generated directory on an ephemeral loopback port and request representative primary, secondary, and changed asset URLs. Assert HTTP status, non-empty body, and content type where relevant. Use a short readiness loop and always terminate the server in cleanup.
7. **Match each interface's result contract.** When a verifier exposes multiple modes—such as a fixture self-test and a production/file CLI—inspect or exercise each mode before writing assertions. Do not assume their JSON keys or exit semantics match: a self-test may return `passed`/`cases`, while file validation may return `valid`/`errors`. For validator libraries, distinguish malformed-object exceptions from well-formed-but-nonconforming comparison results; a subset checker may deliberately return enumerated violations rather than raise. Assert the mode-specific schema, exit code, and at least one representative accepted and rejected input.
8. **Repair verifier failures honestly.** If the temporary verifier has a syntax, quoting, or harness error, classify that as a verifier failure, fix the verifier, and rerun the affected checks. Never report a failed harness assertion as evidence about the implementation.
9. **Clean up.** Remove temporary scripts, fixture files, and temporary servers even when checks fail. Independently confirm the temporary filename pattern is gone when feasible.
10. **Classify the result.** Report the status of each acceptance truth and the final ad-hoc verifier as `passed`, `failed`, `blocked`, or `unresolved`; list the checks and exact failures, and distinguish them from a canonical test/lint suite. Do not issue PASS while any mandatory truth is `unresolved` or `blocked`. `failed` is BLOCK. Only all-`verified` may PASS. Do not call the repository “green” unless the applicable canonical suite actually passed. A passing command with missing truth-to-evidence coverage is not a pass. A secondary checklist cannot rescue a missed blocker.

## Evidence record

Record, at minimum:

- workspace, changed contract, and stable source identity inspected;
- acceptance truths and their required artifact, wiring, and behavioral evidence;
- status of each truth: `verified`, `failed`, `blocked`, or `unresolved`;
- verifier location/prefix and cleanup result;
- source-level checks performed;
- build/generation command and result;
- realistic smoke URLs or artifact checks;
- harness failures and repairs, if any;
- final ad-hoc status and explicit limits;
- commit/deploy state, separately from local verification.

Keep the record concise. The evidence should let a later agent reproduce the important checks without preserving credentials, private content, or a one-off transcript.

When the artifact came from delegated work or supports an external-effect claim, use the shared [Composition contract](../COMPOSITION.md) to identify the producer claim, bound source/run, receipt or handle, downstream verifier, and final reporting owner.

## Fixture and contract adequacy

When a test surface calls a structured file a fixture, verify that it contains enough synthetic input to reproduce the experiment—not merely case IDs, invariants, and expected labels. Require the authenticated task, constant facts or inputs, complete per-case payloads, allowed effects, and non-empty expected outcomes where applicable. Otherwise rename it a registry/specification and state that adapters must supply and record their own payloads.

Add vacuity mutations, not only deletion mutations: empty outcome lists, absent payloads, false or missing invariants, blank limitation sections, and mismatched run/task identities should fail. A canary that protects names while accepting an empty experiment is benchmark theater.

For source-evidence structure, distinguish syntax from truth. A checker may require identity fields, coverage scope, and nonblank limitations, but must not claim that this proves the source was inspected or the coverage claim is accurate.

## Candidate-mechanism trials

Before implementing a proposed evidence or observability mechanism, state the unresolved decision it is supposed to improve and compare it with the **strongest existing evidence path**, not an artificially weak baseline. If current session records, tool receipts, shell output, archived sources, or delivery handles already resolve the case equally well, record a decision-value failure and stop; additional structure has not earned adoption merely because it can encode the incident.

For a vertical trial:

1. Bind the replay to recoverable incident evidence and separate historical facts from authored fixture labels.
2. Require the mechanism to derive its verdict from observations or independently bound receipts. A producer-supplied field such as `process_started=false` or `working_directory=missing` is a claim to verify, not an observation.
3. Test semantic contradictions and permissive parsing: impossible status/exit combinations, unrelated command classes, arbitrary source identities, success strings containing failure text, stale revisions, and mismatched producer/evaluator identities.
4. Enforce privacy on every retained free-text and structured field; measuring packet size or omitting obvious secrets is not privacy enforcement.
5. Reproduce the evidence boundary itself. Rerunning authored code and unit tests does not reproduce a historical incident or prove binding to its source evidence.
6. Treat same-agent or same-model hostile review as **held-out skeptical discrepancy detection**, not independent proof.
7. If component, hostile, composition, privacy, or decision-value gates fail, remove the unearned mechanism rather than hardening redundant infrastructure. Preserve a concise rejection record only when it prevents recurrence or narrows a legitimate future trigger.

A successful negative result is legitimate: a rigorous trial may establish that the existing evidence system already does the job and that the proposed mechanism should remain unimplemented.

## Semantic canaries and evidence receipts

When static validators preserve required guidance or evidence metadata:

- Bind semantic canaries to the owning active section, not merely the whole file. Strip comments and fenced examples, require exactly one owning heading where uniqueness matters, and stop the section at the next heading of equal or higher rank.
- Mutation-test both deletion and **semantic relocation**. A marker moved into an unrelated section must fail even though the phrase still exists somewhere in the artifact.
- Validate receipt declarations against one another: exact scope, contiguous non-overlapping exhaustive partitions, derived counts, retained-manifest hashes, exceptional/blank-item checks, and identity/hash agreement with the source record.
- Label the proof boundary honestly. Internal-consistency checks establish receipt accounting, not source truth, interpretation correctness, or correspondence to an unretained artifact.
- Check scan coverage before trusting a clean result. Apply directory exclusions relative to the repository root, not its absolute ancestors; an empty scan in a nonempty corpus is a verification defect, not a pass.
- Re-check asynchronous review findings against the current commit and repository state before repair or release; a reviewer can accurately report an intermediate conflict state that no longer describes the candidate.

## Pitfalls

- Treating an executor, subagent, or producer summary as verification evidence rather than a claim to resolve.
- Treating human or model "looks good," Lighthouse extras, or a long PASS writeup as a named metric.
- Blending unrelated truths into one quality score so a secondary checklist rescues a missed blocker.
- Issuing PASS while a mandatory truth remains `unresolved` or `blocked`.
- Reusing a receipt after the source revision, dirty-state set, generated bundle, or other bound artifact changed.
- Treating old successful output as proof for a newer diff.
- Calling an ad-hoc verifier a canonical suite or implying broader coverage than it has.
- Assuming an execution wrapper is visible to the evidence recorder without checking the applicable runtime adapter. Successful execution and captured evidence are separate claims.
- Checking only source files while forgetting the generated deploy bundle.
- Using a fixed local port when an ephemeral port avoids collisions and hidden state.
- Leaving a temporary server or verifier file alive after completion.
- Swallowing a verifier syntax error and reporting the site as failed or passed without separating the two.
- Emitting secrets or full private artifacts while constructing evidence.
- Expanding a focused smoke test into a speculative test framework during a visual/content task.

## Support

- See `references/fresh-local-verification.md` for a compact recipe and evidence format.
