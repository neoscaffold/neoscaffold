import { module, test } from 'qunit';
import { setupRenderingTest } from 'neoscaffold/tests/helpers';
import { render, fillIn, click } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';
import Service from '@ember/service';

// A stub litegraph service so the component can be tested without a backend or
// the global NeoScaffold canvas object.
class StubLitegraphService extends Service {
  lastPrompt = null;

  async buildAndInsert(promptText) {
    this.lastPrompt = promptText;
    if (promptText.includes('fail')) {
      throw new Error('boom');
    }
    return {
      result: {
        prompt: {
          1: { type: 'nsString', name: 's', inputs: { text: 'hi' } },
          2: { type: 'ConsoleLog', name: 'l', inputs: { any: { originId: '1' } } },
        },
        plan: ['Create a string.', 'Log the result with ConsoleLog.'],
        warnings: [],
        source: 'offline',
      },
      created: 2,
    };
  }
}

module('Integration | Component | neo-prompt-bar', function (hooks) {
  setupRenderingTest(hooks);

  hooks.beforeEach(function () {
    this.owner.register('service:litegraph', StubLitegraphService);
  });

  test('it renders the prompt input and disabled submit', async function (assert) {
    await render(hbs`<NeoPromptBar />`);
    assert.dom('[data-test-prompt-input]').exists();
    assert.dom('[data-test-prompt-submit]').isDisabled();
  });

  test('building a graph shows the plan and node count', async function (assert) {
    await render(hbs`<NeoPromptBar />`);
    await fillIn('[data-test-prompt-input]', 'log "hello"');
    assert.dom('[data-test-prompt-submit]').isNotDisabled();
    await click('[data-test-prompt-submit]');

    assert.dom('[data-test-prompt-result]').exists();
    assert.dom('[data-test-prompt-plan]').includesText('Log the result');
    assert.dom('[data-test-prompt-result]').includesText('Added 2 node(s)');

    const service = this.owner.lookup('service:litegraph');
    assert.strictEqual(service.lastPrompt, 'log "hello"');
  });

  test('it surfaces build errors', async function (assert) {
    await render(hbs`<NeoPromptBar />`);
    await fillIn('[data-test-prompt-input]', 'please fail');
    await click('[data-test-prompt-submit]');
    assert.dom('[data-test-prompt-error]').hasText('boom');
  });
});
