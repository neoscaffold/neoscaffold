import { module, test } from 'qunit';
import { setupTest } from 'neoscaffold/tests/helpers';

module('Unit | Route | workflow', function (hooks) {
  setupTest(hooks);

  test('it exists', function (assert) {
    let route = this.owner.lookup('route:workflow');
    assert.ok(route);
  });
});
