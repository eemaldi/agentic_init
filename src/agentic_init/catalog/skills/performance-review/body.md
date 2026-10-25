# Performance review

## Inputs
- The change or code path under review, and the workload that matters (request rate, data volume, payload size).

## Procedure
1. State the performance requirement: the operation, the target (p95 latency, throughput, memory, cost) and the workload.
2. Measure the current behaviour before reasoning about it. No measurement: say so and propose how to get one.
3. Look for the usual causes, in this order:
   - N+1 queries and missing indexes
   - work inside loops that could be batched or hoisted
   - unbounded result sets, payloads and caches
   - synchronous I/O on a hot path, and lock contention
   - repeated serialization of the same data
4. Estimate the impact of each finding at the real workload, not at test scale.
5. Propose the smallest change that addresses the dominant cost, and how to measure the difference.
6. Check the change does not trade correctness for speed: concurrency, cache invalidation, partial failure.

## Never
- Optimize without a measurement or a clear complexity argument.
- Introduce a cache before establishing invalidation and staleness limits.

## Report
1. Findings ordered by expected impact, each with the evidence behind it
2. Measurements: before, after, and the workload used
3. Correctness risks introduced by the optimization
4. What was measured and what remains unverified
