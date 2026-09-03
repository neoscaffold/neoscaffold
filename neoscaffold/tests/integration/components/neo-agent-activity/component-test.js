import { module, test } from 'qunit';
import { setupRenderingTest } from 'neoscaffold/tests/helpers';
import { render, waitFor, click } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';
import Service from '@ember/service';

class StubLitegraphService extends Service {
  calls = 0;

  async fetchAgentEvents() {
    this.calls += 1;
    return [
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
    ];
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

  test('toggle collapses the body', async function (assert) {
    await render(hbs`<NeoAgentActivity />`);
    await waitFor('[data-test-agent-body]');
    await click('[data-test-agent-toggle]');
    assert.dom('[data-test-agent-body]').doesNotExist();
  });
});
