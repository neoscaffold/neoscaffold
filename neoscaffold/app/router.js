import EmberRouter from '@ember/routing/router';
import config from 'neoscaffold/config/environment';

export default class Router extends EmberRouter {
  location = config.locationType;
  rootURL = config.rootURL;
}

Router.map(function () {
  if (config.NEOSCAFFOLD_AUTH_ENABLED) {
    this.route('sign-up');
    this.route('sign-in');
  }

  this.route('index', { path: '/' });
  this.route('workflow');
  this.route('directory');
});
