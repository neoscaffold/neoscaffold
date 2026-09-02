import Component from '@glimmer/component';
import { action } from '@ember/object';
import { tracked } from '@glimmer/tracking';
import { inject as service } from '@ember/service';

/**
 * Natural-language entry point for the workflow editor. The user describes what
 * they want; the component asks the backend to build a validated prompt-graph
 * and inserts it onto the canvas, then shows the plan the builder followed.
 */
export default class NeoPromptBarComponent extends Component {
  @service litegraph;

  @tracked promptText = '';
  @tracked status = 'idle'; // idle | building | done | error
  @tracked plan = [];
  @tracked warnings = [];
  @tracked errorMessage = '';
  @tracked createdCount = 0;
  @tracked source = '';

  get isBuilding() {
    return this.status === 'building';
  }

  get canSubmit() {
    return !this.isBuilding && this.promptText.trim().length > 0;
  }

  get isSubmitDisabled() {
    return !this.canSubmit;
  }

  get isDone() {
    return this.status === 'done';
  }

  get isError() {
    return this.status === 'error';
  }

  @action
  updatePrompt(event) {
    this.promptText = event.target.value;
  }

  @action
  async submit(event) {
    if (event && event.preventDefault) {
      event.preventDefault();
    }
    if (!this.canSubmit) {
      return;
    }

    this.status = 'building';
    this.errorMessage = '';
    this.plan = [];
    this.warnings = [];
    this.createdCount = 0;

    try {
      const { result, created } = await this.litegraph.buildAndInsert(
        this.promptText,
      );
      this.plan = result.plan || [];
      this.warnings = result.warnings || [];
      this.source = result.source || '';
      this.createdCount = created;
      this.status = 'done';
    } catch (error) {
      this.errorMessage = error.message || 'Failed to build graph';
      this.status = 'error';
    }
  }
}
