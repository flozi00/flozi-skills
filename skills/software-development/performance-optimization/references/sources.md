# Performance Optimization — Sources

Research basis for the performance-optimization skill (verified 2026-11-23):

- **Brendan Gregg — The USE Method**
  https://brendangregg.com/usemethod.html
  Utilization / Saturation / Errors checklist per resource. Start from
  questions, not from whatever metric happens to be graphed — the fastest way
  to find which resource is actually the bottleneck.

- **Brendan Gregg — Performance Analysis Methodology**
  https://brendangregg.com/methodology.html
  Catalogue of methodologies (streetlight anti-method, drill-down, workload
  characterization, off-CPU analysis) and when each one misleads.

- **Brendan Gregg — Flame Graphs**
  https://brendangregg.com/flamegraphs.html
  Official reference for reading flame graphs: width = frequency, not
  duration; how to spot the hot path and the "plateau" of a blocking call.

- **Use The Index, Luke — SQL Indexing and Tuning**
  https://use-the-index-luke.com/
  B-tree anatomy, composite index column order, why `LIKE '%x'` and functions
  on indexed columns kill the index. Vendor-neutral (Oracle, MySQL,
  PostgreSQL, SQL Server).

- **PostgreSQL — Using EXPLAIN**
  https://www.postgresql.org/docs/current/using-explain.html
  `EXPLAIN` vs. `EXPLAIN ANALYZE`, plan-node costs, row-estimate errors and
  the caveats section (caching, timing overhead). Read before "the query is
  slow" turns into a guess.

- **MDN — HTTP Caching**
  https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
  Freshness vs. validation, `Cache-Control` directives, heuristic caching and
  revalidation. The correctness baseline before adding any cache layer.

- **OpenJDK — JMH (Java Microbenchmark Harness)**
  https://github.com/openjdk/jmh
  Dead-code elimination, warm-up, forking, blackhole consumption. The
  canonical list of ways a hand-rolled microbenchmark lies.

- **google/benchmark**
  https://github.com/google/benchmark
  C++ microbenchmark library: statistical repetitions, complexity
  (`BigO`) estimation, preventing the optimizer from removing the measured
  work.
