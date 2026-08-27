# Fresh local verification recipe

Use this when current workspace evidence is stale or explicitly marked unverified.

## Minimal recipe

1. Identify the current changed paths and the behavior they are meant to preserve.
2. Create a temporary Python verifier with:
   - `tempfile.NamedTemporaryFile(..., prefix="hermes-verify-", delete=False)`;
   - an OS temp directory, not the repository;
   - a top-level direct terminal invocation of the exact generated path;
   - cleanup after that direct run.
   If an evidence hook attributes only direct commands, do not create or invoke the verifier inside `execute_code`, an inline interpreter wrapper, or another child process: the checks may run successfully while remaining invisible to the evidence recorder. Run canonical project checks as separate direct commands.
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
6. Confirm the `hermes-verify-*` temporary file is gone when feasible.

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
