import { module, test } from 'qunit';
import { setupTest } from 'neoscaffold/tests/helpers';

module('Unit | Service | litegraph', function (hooks) {
  setupTest(hooks);

  // TODO: Replace this with your real tests.
  test('it exists', function (assert) {
    let service = this.owner.lookup('service:litegraph');
    assert.ok(service);
  });
});
