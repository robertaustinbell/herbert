# Multi-agent graph gates and recovery

Load only when dispatching a dependent multi-agent graph or reviewing a failed handoff.

## Downstream input contract

Before dispatching a downstream node, compare its required inputs with artifacts the upstream contract actually produces. If an input is missing, ask the producer to supply or validate its own evidence; the coordinator should not author evidence owned by another node.

## Gated handoffs

For dependent nodes, validate the handoff schema and prerequisites before starting the next node. Bind the result to the reviewed input identity; if a protected input changes after review, the prior result is stale. Distinguish invalid data from a validator failure, and diagnose the gate before relaunching.

## Freshness and stop conditions

A frozen test or witness can become stale when the system under test changes. The test owner—not the implementer—should approve a new pin, preserve the original assertions, and require the changed implementation to rerun against it.

A dispatch prompt can narrow a role but cannot override stop conditions. Read the complete hold or stop state before recommending more work. Keep ready and hold states mutually consistent; when a rule requires a hold, stop rather than emitting a contradictory ready signal.
