# Database migration

Schema and data changes are A2 work: plan, implement and verify, then let a human approve. Never run a migration against production yourself.

## Inputs
- The schema or data change, the tables and code that touch it, and the deployment model (rolling, blue/green, downtime window).

## Procedure
1. Read the current schema and the code that reads and writes the affected columns.
2. Choose the sequence. Default to expand/contract:
   - expand: add the new column/table, nullable or defaulted, no reads yet
   - backfill: migrate data in batches, idempotently, resumable after failure
   - switch: write both, then read the new shape
   - contract: drop the old shape only after everything reads the new one
3. Write the migration with the project's migration tool. Never hand-edit a schema that a tool owns.
4. Write the reverse migration, or state explicitly why the step is irreversible and what the recovery is.
5. Verify against a fresh database: apply from empty, apply on a copy with representative data, then apply the reverse.
6. Check the blast radius: locks held, table size, expected duration, concurrent writers, replicas.
7. Run the full suite{% if commands.test %}: `{{ commands.test }}`{% endif %} and any migration-specific tests.

## Never
- Combine a destructive step (drop, rename, type narrowing) with the additive step in one deploy.
- Backfill in a single unbounded statement on a large table.
- Apply a migration to a shared or production database without explicit human approval.

## Report
- The sequence, one line per step, with the deploy each belongs to
- Evidence: migration applied from empty, on a data copy, and reversed
- Lock/duration estimate, rollback plan, and residual risk
