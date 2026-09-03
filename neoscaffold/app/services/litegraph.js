import Service from '@ember/service';

/**
 * Minimal accessor for the portable global `NeoScaffold` instance.
 *
 * The NeoScaffold-specific UI (natural-language prompt bar, Agent Activity
 * panel, canvas insertion) and its backend calls live in
 * `public/scripts/neoscaffold_litegraph_extensions.js` so they stay
 * self-contained and portable. This service just exposes that instance to Ember
 * code/tests that need it.
 */
export default class LitegraphService extends Service {
  get instance() {
    return typeof window !== 'undefined' ? window.NeoScaffold : undefined;
  }
}
