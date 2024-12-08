import Component from '@glimmer/component';
import { inject as service } from '@ember/service';
import goBackPage from '../../utils/go-back-page';
import { action } from '@ember/object';

export default class NavBarComponent extends Component {
  @service router;

  get canBackPage() {
    if (this.router.transitionHistory) {
      return this.router.transitionHistory.length > 0;
    }
    return false;
  }

  @action
  goBack() {
    goBackPage(this.router);
  }
}
