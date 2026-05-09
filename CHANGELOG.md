# Changelog

## 0.2.0 - 2026-05-09

- Added parallel graph execution for async-capable nodes with configurable concurrency.
- Added frontend execution mode controls and per-node runtime status tracking for parallel workflows.
- Added async support for node evaluation, including sync node methods that return awaitables.
- Added soft `GOTO` handling in parallel mode for control-flow graphs, including downstream cache invalidation.
- Updated `IfEqual` and `WhileLoop` control flow to complete through their `End*` nodes in parallel mode while only running the selected branch/body path and deferring `End*` nodes until branch/body work finishes.
- Added acceptance and unit coverage for parallel execution, `IfEqual`, and `WhileLoop` workflows.
