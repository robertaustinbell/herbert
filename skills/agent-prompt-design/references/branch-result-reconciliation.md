# Branch-result reconciliation

Use this before merging structured results from delegated or parallel work.

## Complete input and identity

1. Obtain the complete saved result. A display preview, truncated log, or producer summary is not the complete record; if the full result is unavailable, mark the branch incomplete rather than reconstructing omitted fields from prose.
2. Bind each result to its task, producer, and input/version identity before parsing it.
3. Validate the declared schema and output bound before treating the result as a merge input.

## Coverage and ownership

1. Reconcile the exact assigned-item set: identify missing items, duplicates, unexpected additions, and which producer owns each check.
2. Reconcile evidence references and their provenance. Keep raw proposals separate from independently reviewed final records.
3. If actual outputs exceed the declared bound, update remaining context accounting; do not report that the original bound held.
4. Preserve unresolved, blocked, or missing branches as explicit states. Never count absent output as success.
