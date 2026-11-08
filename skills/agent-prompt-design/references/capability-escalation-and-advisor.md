# Capability escalation and advisor guidance

## When to use

Use only when task coupling, drift risk, verification difficulty, or expensive directional rework may justify coordination cost. This is conditional guidance, not a standing requirement or an evaluation program.

## Decide whether escalation or an advisor is warranted

1. Start with adequate margin, not the cheapest possible attempt. Consider consequence, ambiguity, novelty, reversibility, verification difficulty, and the principal's supervision cost; high-stakes or hard-to-verify work may warrant stronger capability from the outset.
2. Escalate on evidence: progress stalls; two materially different fixes fail; the worker loses the objective or a load-bearing constraint; new system coupling appears; verification stays inconclusive; or retries cost more than escalation. Do not repeat the same failing approach at the same capability level.
3. Use a narrow advisor only when coordination risk justifies it. The advisor tracks objective, constraints, evidence, drift, stop conditions, and verification gaps; it does not duplicate implementation or overrule the merge owner. If worker and advisor share a model, treat errors as correlated and use the role split for structural discipline, not independent error detection.
4. Prefer material intervention receipts over constant narration. Silence means no material intervention, not proof the workflow was flawless.

Positive triggers include at least three substantive dependent steps, multiple systems or artifacts, expensive rework from drift, or verification gaps an independent role can expose. Skip one-shot retrieval, mechanical transformations, trivial tool calls, or cases where an advisor merely duplicates implementation.

## Material receipt

Record only when intervention materially changes action or result, reveals a failure, or creates significant overhead:

Record the fact and decision-relevant effect of any principal correction explicitly; summarize or redact sensitive payloads when exact wording is unnecessary. Do not silently normalize the correction away.

Record the minimum necessary. Prefer stable identifiers and source handles to sensitive payloads; retain receipts only under authorized scope and applicable retention/disposal rules.

```text
Date/task/session:
Trigger:
Configuration: escalation only | advisor + escalation
Material intervention or failure:
Decision/action changed:
Verified result:
Defects or rework:
Principal correction:
Unnecessary escalation or false alarm:
Observed overhead:
Evidence:
```

## Revision conditions

Revise or disable when false alarms, premature escalation, duplicated work, correlated error, or material overhead recur. Disable immediately after a severe safety, privacy, authorization, external-side-effect, or false-verification regression attributable to the hook. Provider cache savings and benchmark rank are secondary signals, never quality proxies.
