import { module, test } from 'qunit';
import { setupTest } from 'neoscaffold/tests/helpers';

module('Unit | Route | privacy-policy', function (hooks) {
  setupTest(hooks);

  test('it exists', function (assert) {
    let route = this.owner.lookup('route:privacy-policy');
    assert.ok(route);
  });
});
