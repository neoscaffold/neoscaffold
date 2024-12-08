import Component from '@glimmer/component';
import { inject as service } from '@ember/service';
import { action } from '@ember/object';

import config from '../../config/environment';
import goBackPage from '../../utils/go-back-page';

export default class AuthGoogle extends Component {
  @service session;
  @service notify;
  @service router;

  @action
  googleAuthentication() {
    try {
      this.load_gsi_script_and_generate_button();
    } catch (error) {
      this.errorMessage = error.error || error;
    }
  }

  google_script_callback() {
    if (window && document && window.google) {
      const scope = this;

      window.google.accounts.id.initialize({
        client_id: config.GOOGLE_SIGN_IN_CLIENT_ID,
        callback: async (data) => {
          data.mode = scope.args.mode;
          await scope.session.authenticate(
            'authenticator:google-sign-in',
            data,
          );
          if (scope.session.isAuthenticated) {
            if (scope.args.mode === 'signup') {
              scope.notify.success('You have been signed up.');
            } else {
              scope.notify.success('You have been signed in.');
            }

            goBackPage(scope.router);
          }
        },
      });
      window.google.accounts.id.renderButton(
        document.getElementById('google-client-button'),
        {
          text: scope.args.mode === 'signup' ? 'signup_with' : 'signin_with', // customization attributes
          width: 240,
          theme: 'filled_black',
        },
      );
    }
  }

  load_gsi_script_and_generate_button() {
    if (window && document) {
      const url = 'https://accounts.google.com/gsi/client';
      const scripts = document.getElementsByTagName('script');
      const isScriptLoaded = Array.from(scripts).some(
        (script) => script.src === url,
      );
      let scope = this;
      if (isScriptLoaded) {
        return this.google_script_callback();
      } else {
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.onload = this.google_script_callback.bind(scope);
        script.defer = true;
        script.async = true;
        script.id = 'google-client-script';
        document.querySelector('body')?.appendChild(script);
      }
    }
  }
}
