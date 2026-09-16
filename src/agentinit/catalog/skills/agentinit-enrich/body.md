# Enrich agent context

Replace placeholders in generated docs with verified knowledge about this repository.

## Procedure
1. Explore the repository: manifests, entry points, directory layout, tests, CI config, deployment files.
2. Fill in, keeping each file concise and factual:
{% if "brownfield" in selected.docs %}
   - `docs/brownfield/system-map.md`, `critical-paths.md`, `invariants.md`, `hotspots.md`, `test-gaps.md`
{% endif %}
{% if "architecture" in selected.docs %}
   - `docs/architecture/system-overview.md`
{% endif %}
   - An `## Architecture` section in `CLAUDE.md` of at most 15 lines, placed **outside** the `agentinit:begin/end` markers.
3. Verify every command you document by running it. Mark anything you cannot verify with `(unverified)`.
4. Do not modify source code, tests, `.claude/` or files between `agentinit` markers.
5. Finish with a summary of what you documented and open questions for the human.
