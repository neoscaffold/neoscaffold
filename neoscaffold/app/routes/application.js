import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class ApplicationRoute extends Route {
  @service session;
  @service fastboot;
  @service router;

  async beforeModel() {
    await this.session.setup();
    if (!this.fastboot.isFastBoot) {
      if (window.NeoScaffold) {
        window.NeoScaffold.applicationRouter = this.router;
        window.NeoScaffold.applicationSession = this.session;
      }
    }
  }
}
