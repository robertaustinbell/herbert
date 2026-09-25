## Decision effect

What observation, recommendation, action, verification, repair, adoption path, or boundary does this change?

## Owning layer and scope

Which file or layer owns the behavior? What is intentionally excluded?

## Strongest objection

What is the best case against this change, including overlap with existing guidance or a simpler alternative?

## Known failure and reversal evidence

How could this add ceremony, overreach, confusion, dependency, or false confidence? What evidence would justify narrowing, reverting, consolidating, or removing it?

## Verification performed

List the checks actually run and their results. Do not claim checks that were planned but not performed.

## Agent assistance

Describe any material agent assistance. Distinguish agent-generated proposals from observations, tests, source checks, and independent human or model review actually performed.

## Contributor checklist

- [ ] I changed the owning layer rather than duplicating authority elsewhere.
- [ ] I regenerated `index.md` if operating thought frontmatter changed.
- [ ] `python3 scripts/generate_index.py --check` passes.
- [ ] `python3 -m unittest discover -s scripts -p 'test_*.py'` passes.
- [ ] `python3 scripts/check_template.py` passes.
- [ ] `python3 skills/agent-prompt-design/scripts/test_context_trial_packet.py` passes.
- [ ] `python3 skills/authority-effect-contracts/scripts/test_contracts.py` passes.
- [ ] `git diff --check` passes.
- [ ] I reviewed the complete diff for unintended scope and malformed prose.
- [ ] I verified citations, command output, changed files, and claimed results against their sources or artifacts.
- [ ] I did not include credentials, personal records, private communications, proprietary material, runtime dumps, machine paths, account identifiers, or sensitive authorization details.
- [ ] Any public submission or external communication was authorized by the responsible person or organization.
