// agent_graph LiteGraph UI hooks.
//
// The Python contracts for PromptNode / BuildGraphNode are enough for the
// default node factory to render them, so this file intentionally adds no
// custom LiteGraph classes yet. It exists so the extension can grow bespoke
// node UI (e.g. a multiline prompt widget) without a backend change.
//
// It is eval'd by the frontend during loadExtensions(); keep it side-effect free.
(function () {
  if (typeof console !== "undefined" && console.debug) {
    console.debug("[agent_graph] extension UI hooks loaded");
  }
})();
