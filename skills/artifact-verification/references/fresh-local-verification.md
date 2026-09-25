# Fresh local verification recipe

Use this when current workspace evidence is stale or explicitly marked unverified.

## Minimal recipe

1. Identify the current changed paths and the behavior they are meant to preserve.
2. Run the applicable canonical checks. If an acceptance truth remains uncovered, create an isolated verifier in the runtime-approved temporary workspace outside the delivered artifact. Bind its execution to the inspected source and remove it afterward. Use the conditional runtime adapter below only when its instrumentation requirements apply.
3. In the verifier:
   - read only the relevant source files;
   - assert exact behavioral markers and counts;
   - run the project build;
   - start a local server on port `0` or another ephemeral loopback port;
   - request representative generated pages and changed assets;
   - assert status, body presence, and content type where meaningful;
   - terminate the server in `finally`.
4. Print a compact machine-readable result, for example:

```text
AD_HOC_VERIFICATION {"errors": [], "status": "passed"}
```

5. If the verifier itself fails, fix and rerun it. Keep harness failures separate from implementation failures.
6. Confirm temporary verifier resources are removed when feasible.

## Conditional Hermes evidence-hook adapter

Use this adapter only when the active Hermes evidence hook requires a prefixed file and direct command attribution. Confirm the current hook contract rather than assuming every Hermes deployment has it.

- Create the verifier with `tempfile.NamedTemporaryFile(..., prefix="hermes-verify-", delete=False)` in the runtime-approved scratch directory. Honor the current environment's temporary-directory policy; do not hard-code a system temp path.
- Invoke the exact generated file through a direct terminal command, then clean it up even if verification fails.
- If the hook observes only direct commands, execution inside `execute_code`, an inline interpreter wrapper, or a nested child process can be real but absent from the captured evidence. Run canonical project checks separately.
- Verify the evidence record, not merely the filename. A prefix or direct invocation alone does not prove the hook captured the execution or the artifact passed.

Runtimes without this hook use their own supported execution and evidence path; they do not inherit its filename convention.

## Named metrics

Before tools, freeze each mandatory truth as its own metric. Prefer a code check when the claim is mechanical. Do not issue PASS while any mandatory truth is `unresolved` or `blocked`.

```text
truths:
  - id: workers-404-runtime
    check: runtime GET of a nested missing path returns HTTP 404 with the branded body
    kind: code
verdict: PASS only if all verified
```

"Looks good" and blended scores are not metrics.

## Reporting boundary

Call this **ad-hoc verification**. Do not call it a canonical test/lint suite, do not claim broad visual coverage from HTTP checks, and do not report a deploy unless deployment and live verification were separately authorized and completed.
