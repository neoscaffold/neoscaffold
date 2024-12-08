import { module, test } from 'qunit';
import { setupRenderingTest } from 'neoscaffold/tests/helpers';
import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';

module('Integration | Component | neo-header', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<NeoHeader />`);

    assert.dom().hasText('');

    // Template block usage:
    await render(hbs`
      <NeoHeader>
        template block text
      </NeoHeader>
    `);

    assert.dom().hasText('template block text');
  });
});
