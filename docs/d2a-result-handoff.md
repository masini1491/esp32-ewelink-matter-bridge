# D2A bounded result handoff

D2A addresses the prior D2 execution-surface gap: a long-running child may finish without its invoking command returning a usable summary. `tools/bounded_result_runner.py` is a local-only, generic direct-child wrapper; it is not an mDNS collector, parser, sanitizer or live-network authorization.

Future authorized callers resolve the repository-local runtime state with `git rev-parse --git-path d2a-runtime`. The runner creates a private `d2a-*` run directory there, stores raw child stdout/stderr only in that Git-local untracked namespace, and writes an atomic `result.json` containing only status, return code, timeout state, duration, byte counts and raw-file basenames. It never stores argv, environment or raw output in `result.json`.

The runner uses argv execution with `shell=False`. It waits for the direct child only; on timeout it terminates, waits briefly, then kills if necessary before finalizing result metadata. It does not guarantee process-tree cleanup: a future wrapped tool must not daemonize or spawn detached workers. `status` reads safe metadata and `cleanup` deletes only runner-owned marked directories.

D2A synthetic validation proves cross-command handoff and cleanup. It does not perform Network, Hardware or Matter validation, and it does not authorize D2 live observation.
