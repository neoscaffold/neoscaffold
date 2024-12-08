import Component from '@glimmer/component';
import { A } from '@ember/array';
import { action } from '@ember/object';
import { tracked } from '@glimmer/tracking';

import config from '../../config/environment';
export default class LitegraphComponent extends Component {
  @tracked
  queueItems = A([]);

  @tracked
  processingQueue = false;

  @action
  async exportGraph(event) {
    event.preventDefault();
    NeoScaffold.exportGraph(); // eslint-disable-line
  }

  @action
  triggerWorkflowInput(event) {
    event.preventDefault();
    document.getElementById('workflow-input').click(); // Programmatically clicks the hidden file input
  }

  @action
  handleWorkflowUpload(event) {
    NeoScaffold.importGraph(event); // eslint-disable-line
  }

  @action
  async createGraph() {
    console.log(config.NEOSCAFFOLD_URL);
    let sessionKey;
    if (config.NEOSCAFFOLD_AUTH_ENABLED) {
      sessionKey = 'userInfo';
    }
    return NeoScaffold.createGraph( // eslint-disable-line
      '#litegraph',
      config.NEOSCAFFOLD_URL,
      sessionKey,
    );
  }

  /**
   * Queue a prompt means to create each prompt an ID make any intermediate changes needed to the graph, send the requests to the backend concurrently, and then capture the response, and use the websocket connection to track the updates between batches and allow the user to see the progress of the prompts.
   * @param {*} missingNodeTypes
   */
  @action
  async queuePrompt(event, batchSize) {
    event.preventDefault();
    return NeoScaffold.queuePrompt(batchSize); // eslint-disable-line
  }

  willDestroyElement() { // eslint-disable-line
    super.willDestroyElement(...arguments);
    // Remove the resize event listener when the component is destroyed
    NeoScaffold.removeEventListeners(); // eslint-disable-line
  }
}
