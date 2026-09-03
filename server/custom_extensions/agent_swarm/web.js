// agent_swarm LiteGraph UI hooks.
//
// The Python contracts for SwarmSolverNode / SwarmJoinNode are enough for the
// default node factory to render them. Per-node agent streams are surfaced in
// the editor's Agent Activity panel (scoped by node id). This file is eval'd by
// the frontend during loadExtensions(); keep it side-effect free.
(function () {
  if (typeof console !== "undefined" && console.debug) {
    console.debug("[agent_swarm] extension UI hooks loaded");
  }
})();
