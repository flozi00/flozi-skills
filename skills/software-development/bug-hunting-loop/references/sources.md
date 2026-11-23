# Bug Hunting Loop — Sources

Research basis for the bug-hunting-loop skill (verified 2026-11-23):

- **Hypothesis — Introduction to Property-Based Testing**
  https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html
  `@given` + strategies, shrinking to a minimal failing example, example
  database for regressions. The reference model for "state the invariant,
  let the generator hunt the counterexample".

- **AFL++ — Fuzzing in Depth**
  https://aflplus.plus/docs/fuzzing_in_depth/
  Three-step fuzzing process (instrument → curate corpus → mutate), corpus
  minimization, dictionary use, parallel fuzzing. Use when the bug class is
  "unexpected input crashes the parser".

- **OSS-Fuzz — Documentation**
  https://google.github.io/oss-fuzz/
  Continuous in-process fuzzing as a service: harness requirements, coverage
  reporting, regression testcase handling. Shows how to keep a fuzz target
  alive in CI instead of running it once.

- **Clang — ThreadSanitizer**
  https://clang.llvm.org/docs/ThreadSanitizer.html
  Data-race detection via compiler instrumentation; ~5–15x slowdown and
  5–10x memory overhead, so race hunting is a separate, targeted run — not
  part of the normal test suite.

- **loom — Concurrency Testing**
  https://docs.rs/loom/latest/loom/
  Exhaustively permutes thread interleavings under the C11 memory model with
  state reduction. The model for deterministic reproduction of a race that
  only fires under one schedule.

- **rr — Record and Replay Debugging**
  https://rr-project.org/
  Deterministic record/replay of multi-process workloads, gdb scripting and
  IDE integration. Turns a once-in-a-thousand-runs failure into a repeatable
  debugging session.

- **Google Testing Blog — Test Sizes**
  https://testing.googleblog.com/2010/12/test-sizes.html
  Small / medium / large by resource access rather than by "unit vs.
  integration" naming. Gives a shared vocabulary for deciding which layer a
  new regression test belongs in.
