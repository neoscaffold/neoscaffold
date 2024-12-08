import BaseAuthenticator from 'ember-simple-auth/authenticators/base';
import { service } from '@ember/service';

import config from '../config/environment';

export default class GoogleSignInAuthenticator extends BaseAuthenticator {
  @service session;
  @service notify;
  @service fastboot;
  @service router;

  async authenticate(data) {
    // use python to get user info

    const url =
      data.mode === 'signup' ? '/auth/sign-up/google' : '/auth/sign-in/google';

    const response = await fetch(config.NEOSCAFFOLD_URL + url, {
      method: 'POST',
      body: JSON.stringify({
        token: data.credential,
      }),
    });

    const responseJson = await response.json();

    if (!responseJson.user_info) {
      this.notify.error('Failed to sign in with Google. Please try again.');
      return {};
    }

    const userInfo = responseJson.user_info;

    const fullUserInfo = {
      authenticator: 'google-sign-in',
      uid: userInfo.email,
      token: data.credential,
      ...userInfo,
    };
    this.session.currentUser = fullUserInfo;

    // save user info to local storage
    localStorage.setItem('userInfo', JSON.stringify(fullUserInfo));

    // NOTICE: DO NOT include [authenticator, uid, token] or it breaks
    return userInfo;
  }

  async invalidate() {
    localStorage.removeItem('userInfo');
    this.session.currentUser = undefined;
    return;
  }

  async restore() {
    if (this.fastboot.isFastBoot) {
      return {};
    }

    let userInfo = localStorage.getItem('userInfo');
    userInfo = JSON.parse(userInfo);

    // check if user is expired
    if (
      userInfo.expiration &&
      userInfo.expiration < new Date().getTime() / 1000
    ) {
      this.notify.error('Your session has expired. Please sign in again.');
      this.session.invalidate();
      localStorage.removeItem('userInfo');
      this.router.transitionTo('sign-in');
      return {};
    }

    // NOTICE: DO NOT include [authenticator, uid, token] or it breaks

    delete userInfo.authenticator;
    delete userInfo.uid;
    delete userInfo.token;

    return userInfo;
  }
}
