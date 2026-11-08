# Prompt-design failure patterns

## Diagnostic use

Use these as diagnostic hypotheses, not automatic explanations:

- **Prompt polishing before problem definition:** adjectives cannot repair an unverifiable objective.
- **Context dumping:** more tokens can reduce attention and increase conflict.
- **Process micromanagement:** brittle prompts block adaptation to observations.
- **Missing authority boundary:** an available action may be mistaken for an authorized one.
- **Self-grading as proof:** confidence is not evidence.
- **Moving the bar:** the proposer lowers thresholds, edits expected output, or drops a failing case and reports improvement.
- **Trace-success substitution:** correct reasoning or tool behavior is accepted despite a stale, incomplete, or wrong delivered artifact.
- **Flake deletion:** variable cases are removed before locating variance in the candidate, judge, tool, or environment.
- **Unbounded retries:** repeated failure without new information rarely becomes wisdom.
- **Premature multi-agent graphs:** coordination cost exceeds useful parallelism.
- **Examples as hidden requirements:** the model copies surface form and misses intent.
- **Provider folklore:** guidance for one model family is treated as universal.
- **No version/evaluation trail:** prompt changes accumulate without knowing which helped.
