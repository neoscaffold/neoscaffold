import Controller from '@ember/controller';
import { tracked } from '@glimmer/tracking';
import config from '../config/environment';

export default class ApplicationController extends Controller {
  @tracked authEnabled = config.NEOSCAFFOLD_AUTH_ENABLED;
}
