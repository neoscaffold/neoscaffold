import Component from '@glimmer/component';
import { service } from '@ember/service';
import { action } from '@ember/object';
import { tracked } from '@glimmer/tracking';

import config from '../../config/environment';

export default class NeoHeaderComponent extends Component {
  @service session;

  @tracked authEnabled = config.NEOSCAFFOLD_AUTH_ENABLED;

  @action
  signOut(e) {
    e.preventDefault();
    console.log(this.session);
    this.session.invalidate('authenticator:google-sign-in');
    console.log('signed out');
    console.log(this.session.isAuthenticated);
  }
}
