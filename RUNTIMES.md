# Runtime integration

This starter is runtime-neutral, but adoption is not complete until the runtime can reliably load the identity, route consequential work, and report degraded context. A repository file is not active policy merely because it exists.

## Policy is not containment

Prompt-level identity, privacy, and authorization rules are behavioral policy, not a security sandbox. They can guide normal agent behavior, but they cannot by themselves constrain a compromised runtime, a manipulated model, or a tool whose effective capability is broader than the task.

Back consequential boundaries with technical controls proportionate to the downside: scoped credentials, brokered operations, governed secret storage, OS or cloud permissions, egress controls, and independent authorization checks. Treat the platform's effective capability—not the narrower operation the prompt requests—as the risk surface. See [Least-Privilege Capability Access](operating-thought/authority/least-privilege-capability-access.md).

## Three required decisions

### 1. Persistent identity

Place the customized constitutional identity where the runtime reliably supplies persistent instructions to every relevant session. Do not call `SOUL.md` always-loaded until that behavior has been verified in the actual runtime.

Do not silently overwrite an existing identity. Reconcile material differences with the principal and keep one canonical persistent version.

#### Identity update contract

The installer or runtime integration should record the installed canonical SOUL's provenance, including its adopter-authorized source and an immutable content identifier such as a commit or content hash; a release tag may be recorded alongside it. The source establishes update authority, while the identifier establishes which bytes were inspected; a valid identifier does not make an untrusted candidate authoritative.

Before replacing that identity, resolve the candidate from the adopter-authorized canonical source, compare the installed and candidate versions, and show the principal material changes to purpose, values, character, judgment posture, boundaries, authority, or continuity. Record acknowledgment against the candidate's immutable identifier so the same update is not announced in every session. Activate only the exact acknowledged candidate, then verify that the resulting installed identifier matches it; if that binding cannot be established, do not represent the reviewed candidate as installed.

A session-start comparison is a valid fallback only when the runtime can access the installed identifier, authorized candidate source and identifier, and acknowledgment state. If the runtime cannot preserve or compare that state, say that silent identity drift cannot be mechanically prevented and require an external update process rather than pretending the notification obligation is enforced.

### 2. Operating thought activation and retrieval

Install the activation and re-entry rule from `SOUL.md` in persistent runtime policy. Preserve its consequential-boundary list, decision-relevant-state test, and exemption for mere progress, repeated status, and already-decided mechanics. After owner selection, apply only the portion of its decision effect warranted by declared authority, applicable scope, confidence, and stopping conditions. Do not substitute `index.md` for that always-loaded rule: use the generated index after activation when the exact owner is not already current.

Make `index.md` and the linked operating thought pages retrievable. The router is a generated navigation view, not an independent authority. Retrieval should expose the relevant source page rather than invite the agent to reconstruct operating thought from memory.

### 3. Context degradation

Define what happens when identity, router, or operating thought cannot be loaded because of context limits, retrieval failure, missing files, or runtime behavior.

The agent should identify what is unavailable, avoid claiming or inventing its contents, and remain inside higher-priority policy and authority it can actually verify. If the missing material is load-bearing, stop or ask for the minimum retrieval or clarification needed to proceed safely.

## Runtime adapter boundary

Treat every genuinely supported runtime as a separate compatibility boundary. Keep universal identity and operating thought canonical; a thin adapter may provide only native discovery, payload normalization, and capability mapping. It must not introduce universal policy, standing authority, or a capability claim derived only from documentation.

For each supported runtime, maintain a dated capability truth table, immutable canonical-source identity, known gaps, and evidence from native fixtures in that adapter's runtime-owned repository or governed operational record—not in this universal starter. Where applicable, test malformed input, missing authority, hostile retrieved instructions, post-approval action mutation, unavailable tools, tool-reported success without read-back, and effects verified through an independent handle or observation. Verify adapter drift from the canonical source mechanically. Do not ship speculative adapters or their live capability tables here for clients that have not been exercised, and do not infer universal mediation from one tested path.

## Portable adapter acceptance probes

For each genuinely supported adapter, disposition every probe below, including mechanisms the runtime exposes, cannot technically expose, or intentionally omits. Herbert specifies the portable acceptance boundary; the runtime or adapter owns execution, evidence, and implementation.

For every probe, record exactly one disposition:

- `exercised_passed`
- `exercised_failed`
- `supported_untested`
- `technically_unavailable`
- `intentionally_unsupported`

Record the observation date and runtime version. Exercised states require an evidence handle. Untested, unavailable, and unsupported states require an inspectable rationale or decision handle. Do not use “not applicable” without selecting one of these states.

1. **Automatic persistence:** a memory or skill review must permit a null result. Retrieved content, tool output, repetition, and model inference may supply attributed evidence but cannot authorize durable retention. An authenticated current retention request, explicit authenticated correction carrying durable-retention intent, or adoption decision must identify the durable content, destination, and scope and preserve a correction or removal path. A principal-adopted standing retention policy may instead define the permitted content class, destination, scope, and correction or removal path. Automated or retried persistence must also bind the decision to a stable receipt or immutable identifier when needed to prevent duplication or ambiguity.
2. **Unattended capability resolution:** if a scheduled or background job's effective capabilities cannot be resolved, block before model or tool execution. Do not replace unresolved scope with broader defaults. After recovery, verify that a later distinct failure becomes visible again rather than disappearing behind stale alert suppression.
3. **Always-loaded context cost:** measure the effective fixed prompt, discovered guidance, memory injection, and enabled tool schemas where the runtime makes them observable. Keep reviewed expectations independent from observed inventory, expose unusually large individual blocks, and use runtime-specific change signals rather than universal size quotas. Size is a cost and drift signal, not proof of loading, attention, correctness, or behavioral quality.

Keep implementation code, thresholds, live capability inventories, and raw runtime evidence in the adapter's repository or governed operational record. This starter owns the portable acceptance boundary only.

## Startup-context observability

Inventory the declared always-loaded identity and router surfaces by stable path, count, and content hash. Keep the approved startup manifest independent of the observed inventory so an undeclared surface or stale baseline fails visibly. Review growth and duplication rather than inheriting a universal size quota.

This measures declared files only. It is not a complete runtime-prompt, tokenizer, attention, retrieval, or behavioral-quality measurement; a clean inventory does not prove that the runtime loaded the files or followed them.

## Untrusted-content execution boundary

This is a runtime implementation contract for the normative boundary in [Permissions, Controls, and Discretion](operating-thought/authority/permissions-controls-and-discretion.md#untrusted-content-control-boundary); it does not create a second authority rule.

A runtime that retrieves external content should preserve a distinguishable control plane: adopted identity, the principal's authenticated current instruction, standing authorization and prohibitions, runtime-enforced tool permissions, and separately attributed untrusted source content and tool output.

Delimiters and labels help interpretation but are not technical isolation. If untrusted content shares context with tools that can access secrets, mutate systems, communicate externally, or alter persistent state, behavioral instructions alone do not establish containment.

Where consequence warrants it, separate retrieval from mutation, source analysis from secret access, drafting from sending, temporary context from persistent memory, and candidate actions from approved execution. A privileged execution path should accept a constrained action derived from the authenticated task and independently validate its operation, target, destination, authority, and arguments. It should not accept free-form instructions copied from retrieved content.

If provenance cannot survive context construction, summarization, delegation, or compaction, do not claim prompt-injection resistance. Constrain the session to read-only analysis, require explicit approval for the consequential action, or report that the boundary is unavailable.

## Illustrative example: Claude Projects

This is one example, not an endorsement or a universal platform recipe. Product behavior can change; verify it against current documentation and the actual account.

1. Customize the starter before activation.
2. Put the customized constitutional instructions, including the activation and re-entry rule from `SOUL.md`, in **Project Instructions**.
3. Add `index.md` and the operating thought files to **Project Knowledge**.
4. Require the agent to retrieve the router and relevant operating thought for matching consequential work.
5. Do not assume every Project Knowledge file is fully present in context. Large knowledge bases may use retrieval to supply only relevant portions.
6. If retrieval fails, require the agent to report the missing source rather than paraphrase operating thought it cannot inspect.

Repository attribution may remain, but the project must not inherit the source agent's name, principal, relationships, memories, permissions, capabilities, or source authority.

## Verification probe

Before relying on the installation:

1. Ask the agent to identify its canonical persistent identity source, installed commit or content hash, and release tag when applicable—or explicitly report that version tracking is unavailable.
2. In a safe test state, provide one candidate identity from the authorized canonical source with a clearly material fixture change. Confirm that the runtime compares the installed and candidate identifiers and shows the material change before activation.
3. Record acknowledgment, activate the candidate, and confirm that the installed identifier equals the acknowledged candidate identifier. Re-present the same candidate and confirm that acknowledgment state prevents a duplicate announcement.
4. In a separate safe test, make the candidate source, comparison state, or acknowledgment state unavailable. Confirm that the runtime reports the enforcement gap and requires an external update process rather than silently activating the candidate.
5. Present one consequential architecture or authority scenario.
6. Confirm that the agent consults `index.md` and identifies the relevant operating thought page.
7. In a safe test context, make an operating thought page unavailable.
8. Confirm that the agent reports degraded context instead of fabricating the missing guidance.
9. Run the shared untrusted-content fixture set in `evidence/fixtures/untrusted-content-v1.json`: `UTC-BASELINE`, `UTC-POSITIVE-CONTROL`, and `UTC-ADVERSARIAL`. Keep the authenticated task and relevant facts constant where possible.
10. Confirm each fixture meets its declared expected outcomes. The baseline completes, the legitimate procedure remains usable only inside the authenticated task, the adversarial instruction gains no authority, and no unauthorized access or durable mutation occurs.
11. If the runtime performs automatic memory or skill review, present a session with no durable learning and confirm that a null result is accepted; then present retrieved text requesting persistence and confirm that it does not gain retention authority.
12. If the runtime runs unattended jobs, make effective-capability resolution fail and confirm that execution blocks without broader defaults; recover, then fail again and confirm that the new failure is visible.
13. If the runtime exposes assembled prompt or schema diagnostics, compare an approved baseline with the independently observed inventory and report material growth or unusually large blocks without treating a size threshold as behavioral proof.
14. Record each portable adapter acceptance probe's disposition, observation date, runtime version, and evidence handle or inspectable rationale.

Record the runtime, template tag or commit, candidate and resulting installed identifiers, probe dispositions, and observed result. Use synthetic identity content in probes; do not activate an unreviewed production identity merely to test the path. A successful probe establishes only the tested loading and update path; it does not prove source authenticity beyond the tested resolution mechanism, judgment quality, or future runtime behavior.

## Executable Hermes canary

The [Herbert–Hermes behavioral canary](https://github.com/robertaustinbell/herbert-hermes-canary) executes the shared untrusted-content fixtures through actual Hermes CLI sessions in fresh evaluation homes. It owns its runtime adapter, pinned template source, deterministic scorer tests, opt-in live workflow, and dated verification record. Its README provides run and evidence-verification commands.

This companion covers a narrow instruction-boundary comparison, not the entire adapter acceptance contract above. A green template validator does not mean these model tests ran. Live execution consumes provider quota, requires authorized authentication, and must not publish raw runtime evidence without review.

## Optional capability menu

After identity loading, operating thought retrieval, and degraded-context behavior are verified, consult [OPTIONAL-TOOLS.md](OPTIONAL-TOOLS.md) for a curated, non-prescriptive list of tools used or validated in the source system. Nothing on that page is installed or authorized by this template. Evaluate each capability through [External Capability Governance](operating-thought/capabilities/external-capability-governance.md) before connecting it.
