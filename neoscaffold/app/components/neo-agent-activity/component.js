import Component from '@glimmer/component';
import { action } from '@ember/object';
import { tracked } from '@glimmer/tracking';
import { inject as service } from '@ember/service';

/**
 * Visibility panel: shows recent agent/subagent activity (graph builds and the
 * per-node subagents they spin up) so users can see inside the swarm. Polls the
 * backend `/v1/agent/events` endpoint while mounted.
 */
export default class NeoAgentActivityComponent extends Component {
  @service litegraph;

  @tracked events = [];
  @tracked streams = [];
  @tracked open = true;
  @tracked errorMessage = '';

  _timer = null;

  get hasStreams() {
    return this.streams.length > 0;
  }

  get count() {
    return this.events.length;
  }

  get hasEvents() {
    return this.events.length > 0;
  }

  @action
  async start() {
    await this.refresh();
    this._timer = setInterval(() => this.refresh(), 2000);
  }

  @action
  stop() {
    if (this._timer) {
      clearInterval(this._timer);
      this._timer = null;
    }
  }

  @action
  toggle() {
    this.open = !this.open;
  }

  @action
  async refresh() {
    try {
      const { events, streams } = await this.litegraph.fetchAgentActivity(100);
      // Newest first for display; child "node" spans keep their parent link.
      this.events = events.slice().reverse();
      this.streams = streams;
      this.errorMessage = '';
    } catch (error) {
      this.errorMessage = error.message || 'failed to load activity';
    }
  }
}
