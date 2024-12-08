import { inject as service } from '@ember/service';
import BaseRoute from './base-route';

import config from '../config/environment';

export default class AuthenticatedRoute extends BaseRoute {
  @service fastboot;
  @service session;
  @service notify;

  beforeModel(transition) {
    super.beforeModel(transition);
    if (!this.fastboot.isFastBoot) {
      if (!config.NEOSCAFFOLD_AUTH_ENABLED) {
        return;
      }
      if (!this.session.isAuthenticated) {
        this.notify.info('You need to be logged in to continue');
        this.router.transitionTo('sign-in');
      }
    }
  }
}
