import { module, test } from 'qunit';
import { setupRenderingTest } from 'neoscaffold/tests/helpers';
import { render, waitFor, click } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';
import Service from '@ember/service';

class StubLitegraphService extends Service {
  calls = 0;

  async fetchAgentActivity() {
    this.calls += 1;
    return {
      events: [
        {
          id: 'ae-1',
          parent_id: null,
          kind: 'graph_build',
          name: 'log "hi"',
          status: 'succeeded',
        },
        {
          id: 'ae-2',
          parent_id: 'ae-1',
          kind: 'node',
          name: 'ConsoleLog',
          status: 'succeeded',
        },
      ],
      streams: [
        {
          node_id: 'solver-1',
          name: 'cf codeforces/409/F',
          text: '[agent] generating solution...\nverified=True',
        },
      ],
    };
  }
}

module('Integration | Component | neo-agent-activity', function (hooks) {
  setupRenderingTest(hooks);

  hooks.beforeEach(function () {
    this.owner.register('service:litegraph', StubLitegraphService);
  });

  test('it renders recent subagent events', async function (assert) {
    await render(hbs`<NeoAgentActivity />`);
    await waitFor('[data-test-agent-event]');
    assert.dom('[data-test-agent-event]').exists({ count: 2 });
    assert.dom('[data-test-agent-activity]').includesText('graph_build');
    assert.dom('[data-test-agent-activity]').includesText('ConsoleLog');
    assert.dom('[data-test-agent-toggle]').includesText('Agent Activity (2)');
  });

  test('it renders per-node agent streams', async function (assert) {
    await render(hbs`<NeoAgentActivity />`);
    await waitFor('[data-test-agent-stream]');
    assert.dom('[data-test-agent-stream]').exists({ count: 1 });
    assert.dom('[data-test-agent-streams]').includesText('cf codeforces/409/F');
    assert.dom('[data-test-agent-streams]').includesText('verified=True');
  });

  test('toggle collapses the body', async function (assert) {
    await render(hbs`<NeoAgentActivity />`);
    await waitFor('[data-test-agent-body]');
    await click('[data-test-agent-toggle]');
    assert.dom('[data-test-agent-body]').doesNotExist();
  });
});
