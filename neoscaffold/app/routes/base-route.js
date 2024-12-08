import Route from '@ember/routing/route';
import { A } from '@ember/array';
import { inject as service } from '@ember/service';

export default class BaseRoute extends Route {
  @service fastboot;
  @service router;

  beforeModel(transition) {
    if (!this.fastboot.isFastBoot) {
      const transitionHistory = this.router.transitionHistory;
      if (!transitionHistory) {
        this.router.transitionHistory = A([transition]);
      } else {
        transitionHistory.pushObject(transition);
      }
    }
  }
}
