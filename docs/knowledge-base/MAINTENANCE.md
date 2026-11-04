# Maintenance

1. Record current main, the candidate head and changed paths. Separate documentation, editorial consistency and mechanics changes.
2. Read the affected committed source and evidence. Preserve the [principles](PRINCIPLES.md), exact variant and uncertainty; identify any inference rather than presenting it as a quotation.
3. Sweep repeated instructions in summaries, tables and prose. Reconcile the entire affected claim without expanding the scope of its evidence.
4. Run the applicable checks below and review the final diff. Report passed, failed and unrun checks separately; software tests do not establish game truth.
5. Distinguish a local candidate, public PR, merged commit, successful deployment and observed live content. A result applies to the tested source identity, not automatically to later edits.

## Current checks

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p 'test_*.py' -v
```

The [Guide checks workflow](../../.github/workflows/guide-checks.yml) runs that discovery command on PRs, including drafts. Main contains tests for selected bow corrections, editorial consistency, model arithmetic, Guide integrity, roadmap accessibility markup, Sapphire evidence and Lamordia handling. The [model](../../tools/bowmodel.py) supplies the shipped scenarios; compare all complete output tuples when checking preservation. Do not substitute an old test count for running current discovery. There is no `tools/qc.py` entrypoint on the checkpointed main.

Integrity tests check the current snapshot, unique IDs, internal anchors and Guide-relative assets. They do not check all historical snapshots, external URLs, CSS URLs, srcset or actual rendering. For documentation, validate relative paths and fragments, review external targets against actual repository records, and scan for private information and unsupported status claims. Use browser checks for affected layout and interactions; an unavailable viewport is unverified, not a pass.

## Versions and deployment

For Guide content, follow [README updating rules](../../README.md#updating): update the build stamp and generate a matching new snapshot without overwriting history. Documentation-only work leaves `index.html`, its stamp and snapshot unchanged.

The [Pages workflow](../../.github/workflows/pages.yml) runs on main pushes and manual dispatch. A docs-only merge therefore still triggers deployment, although Guide runtime bytes should stay identical. Verify deployment separately; this workflow does not run the test suite. Before merging, check the exact head, current repository rules and unresolved reviews rather than assuming an earlier status still applies.
