import Service from '@ember/service';
import config from 'neoscaffold/config/environment';

/**
 * Thin, testable seam over the global `NeoScaffold` LiteGraph object and the
 * backend v1 agent API. Keeping this in a service (rather than only in the
 * monolithic global script) gives components a mockable dependency and a home
 * for the natural-language entry point.
 */
export default class LitegraphService extends Service {
  get baseUrl() {
    return config.NEOSCAFFOLD_URL;
  }

  /**
   * The global NeoScaffold instance, when the canvas script has loaded.
   */
  get instance() {
    return typeof window !== 'undefined' ? window.NeoScaffold : undefined;
  }

  /**
   * Turn a natural-language prompt into a validated prompt-graph via the
   * backend. Returns the parsed JSON `{ prompt, layout, plan, warnings,
   * repairs, source }` or throws with the server's error message.
   */
  async buildGraphFromPrompt(promptText) {
    const response = await fetch(`${this.baseUrl}/v1/agent/build-graph`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: promptText }),
    });

    if (!response.ok) {
      let message = response.statusText;
      try {
        const body = await response.json();
        message = body.error || message;
      } catch (error) {
        // keep the status text
      }
      throw new Error(message);
    }

    return response.json();
  }

  /**
   * Insert an agent-built graph onto the current canvas. Returns the number of
   * nodes created (0 when the canvas is not ready).
   */
  insertGraph(result) {
    const instance = this.instance;
    if (instance && typeof instance.importPromptGraph === 'function') {
      return instance.importPromptGraph(result);
    }
    return 0;
  }

  /**
   * Build from a prompt and insert the result in one call.
   */
  async buildAndInsert(promptText) {
    const result = await this.buildGraphFromPrompt(promptText);
    const created = this.insertGraph(result);
    return { result, created };
  }

  /**
   * Fetch recent agent/subagent activity events for the visibility panel.
   */
  async fetchAgentEvents(limit = 100) {
    const { events } = await this.fetchAgentActivity(limit);
    return events;
  }

  /**
   * Fetch both agent events and the per-node live streams in one call.
   * Returns `{ events, streams }` where `streams` is a list of
   * `{ node_id, name, text }` scoped to each agent's node.
   */
  async fetchAgentActivity(limit = 100) {
    const response = await fetch(
      `${this.baseUrl}/v1/agent/events?limit=${encodeURIComponent(limit)}`,
    );
    if (!response.ok) {
      throw new Error('failed to fetch agent activity');
    }
    const body = await response.json();
    return {
      events: body.events || [],
      streams: Object.values(body.streams || {}),
    };
  }
}
