# Interrupted delegation recovery

Use for long delegated work that may be interrupted or exceed one execution window.

## Before dispatch

- Make the work resumable with durable progress notes, stable input identity, and structured results. Have the worker validate claimed state and append a checkpoint after each meaningful phase.
- For measurement-heavy work, preserve each result as it is produced instead of waiting for a final report.
- Define the authorized executor, scope, and continuation boundary in the task contract.

## After interruption

1. Inspect the run record, available result history, and workspace before retrying.
2. Classify work as complete, partial, or missing; verify current inputs and artifact state.
3. Resume only missing work, preserving valid artifacts. Do not repeat completed fan-out merely because one branch is missing.
4. Treat adjacent warnings as hypotheses, not causes. Broader restarts require evidence and an authorized blast radius.
5. If only the final report is missing, continue with a write-up-only task rather than repeating completed analysis.
6. Continue only through an executor that preserves the original authority and capability limits. Do not resume through a broader path to save time.
