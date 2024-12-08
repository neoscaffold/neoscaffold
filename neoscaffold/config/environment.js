'use strict';

module.exports = function (environment) {
  const ENV = {
    modulePrefix: 'neoscaffold',
    environment,
    rootURL: '/',
    locationType: 'history',
    EmberENV: {
      EXTEND_PROTOTYPES: false,
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. EMBER_NATIVE_DECORATOR_SUPPORT: true
      },
    },

    APP: {
      // Here you can pass flags/options to your application instance
      // when it is created
    },
  };

  if (environment === 'development') {
    // ENV.APP.LOG_RESOLVER = true;
    // ENV.APP.LOG_ACTIVE_GENERATION = true;
    // ENV.APP.LOG_TRANSITIONS = true;
    // ENV.APP.LOG_TRANSITIONS_INTERNAL = true;
    // ENV.APP.LOG_VIEW_LOOKUPS = true;

    ENV.fastboot = {
      hostWhitelist: [/^localhost:\d+$/, /.*run.app.*/],
    };
  }

  if (environment === 'test') {
    // Testem prefers this...
    ENV.locationType = 'none';

    // keep test console output quieter
    ENV.APP.LOG_ACTIVE_GENERATION = false;
    ENV.APP.LOG_VIEW_LOOKUPS = false;

    ENV.APP.rootElement = '#ember-testing';
    ENV.APP.autoboot = false;

    ENV.fastboot = {
      hostWhitelist: [/^.*\.neoscaffold\.com$/, /^localhost:\d+$/],
    };
  }

  if (environment === 'production') {
    // here you can enable a production-specific feature
    ENV.fastboot = {
      hostWhitelist: [/^.*\.neoscaffold\.com$/, /^localhost:\d+$/],
    };
  }

  ENV.NEOSCAFFOLD_URL = process.env.NEOSCAFFOLD_URL || 'http://localhost:6166';

  const neoscaffold_auth_env = (
    process.env.NEOSCAFFOLD_AUTH_ENABLED || ''
  ).toLowerCase();
  ENV.NEOSCAFFOLD_AUTH_ENABLED = neoscaffold_auth_env === 'true';

  ENV.GOOGLE_SIGN_IN_CLIENT_ID = process.env.GOOGLE_SIGN_IN_CLIENT_ID;

  return ENV;
};
