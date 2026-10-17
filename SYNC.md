# Synchronization model

This repository is a curated public projection of a private agent architecture. It is deliberately **not** a mirror.

## Update trigger

Every material change to the source agent's constitutional identity, governance, active operating thought, routing, or reusable operating principles receives a public-impact review in the same work cycle.

The review has two valid outcomes:

1. **Transferable change:** generalize it, update this repository, run the public-boundary checks, publish it, and verify a fresh clone.
2. **No public delta:** keep the private change private because it concerns personal continuity, local capabilities, domain records, evidence, paths, permissions, or history rather than reusable architecture.

No empty parity commit is required. Commit counts and histories are intentionally independent.

## Canonical branch and historical checkpoints

The current default branch is the maintained public artifact. Commit and push transferable improvements as they are ready; use an exact commit when a reproducible identity is needed. Do not create routine semantic-version or point releases. This living template does not promise package compatibility, supported release branches, or backported fixes merely because a tag exists.

Existing tags and GitHub releases remain immutable historical snapshots. A future tag or release is justified only for a deliberately named compatibility, migration, security, archival, or major public checkpoint with an explicit audience and guarantee. Before creating one, review the complete intended delta and bind the tag, notes, CI, and fresh-clone verification to one exact commit.

## Projection boundary

A public update may carry:

- constitutional posture and character;
- agency, privacy, integrity, and authorization boundaries;
- reusable operating thought;
- source-authority and knowledge-placement rules;
- adoption and customization procedures;
- deterministic routing and integrity checks.

It must not carry:

- biography, relationships, preferences, or domain records;
- memories, sessions, messages, evidence cases, or private history;
- credentials, permissions, capability state, or local configuration;
- machine paths, private repository references, or private provenance;
- authority granted in the source relationship;
- language that causes an adopting agent to impersonate the source agent.

## Public-update checks

Publication has two complementary check layers:

- **Public, reproducible checks:** this repository checks generic secret/path patterns, portable identity boundaries, metadata, links, routing, and protected content. It does not publish the source maintainer's private deny-list.
- **Private maintainer checks:** before publication, the maintainer scans the complete candidate public tree, including its checker and scripts, against private identity, organization, path, and environment-residue patterns. Private policy remains outside this repository. Approved attribution exceptions must be narrow; an exact reviewed license-content identity is not an exemption for arbitrary future license text.

The private gate is a maintainer workflow requirement, not a public runtime dependency or an automatically enforced push barrier. A standalone adopter can reproduce the public checks and supply a private gate for its own context. Current-tree checks do not erase or certify Git history, and passing either layer does not prove semantic sanitization. Review the exact staged artifact and rerun both applicable layers against the final publication tree; ignored untracked files are not part of the private worktree scanner's candidate set and must not be added later without review.

Before every public update:

1. inspect the private change semantically;
2. extract only the class-level decision effect;
3. depersonalize by meaning, not blind replacement;
4. regenerate derived files from canonical frontmatter;
5. run `python3 scripts/check_template.py`;
6. run syntax, link, staged-diff, secret-pattern, and semantic reviews;
7. push only to the intended public remote;
8. clone the public HTTPS URL into a fresh directory and rerun validation;
9. verify local and remote heads, public visibility, and template status.

Static checks establish packaging integrity. They do not prove that an adopted agent will exercise good judgment.
