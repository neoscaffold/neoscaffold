import { inject as service } from '@ember/service';
import BaseRoute from './base-route';

export default class RegisteredRoute extends BaseRoute {
  @service fastboot;
  @service session;
  @service notify;

  beforeModel(transition) {
    super.beforeModel(transition);

    if (!this.fastboot.isFastBoot) {
      if (this.session.isAuthenticated) {
        this.notify.info('You are already signed in!');
        this.router.transitionTo('index');
      }
    }
  }
}
