'use strict';

const fs = require('fs');
const path = require('path');
const EmberApp = require('ember-cli/lib/broccoli/ember-app');

module.exports = function (defaults) {
  const fontAwesomeScssDir = path.join(
    __dirname,
    'fontawesome-pro-6.7.2-web/scss',
  );
  const fontAwesomeWebfontsDir = path.join(
    __dirname,
    'fontawesome-pro-6.7.2-web/webfonts',
  );
  const app = new EmberApp(defaults, {
    sassOptions: {
      extension: 'scss',
      includePaths: [fontAwesomeScssDir],
    },
  });

  for (const fontFileName of fs.readdirSync(fontAwesomeWebfontsDir)) {
    app.import(path.join(fontAwesomeWebfontsDir, fontFileName), {
      destDir: 'webfonts',
    });
  }

  const { Webpack } = require('@embroider/webpack');
  return require('@embroider/compat').compatBuild(app, Webpack, {
    staticAddonTestSupportTrees: true,
    staticAddonTrees: true,
    staticHelpers: true,
    staticModifiers: true,
    staticComponents: true,
    staticEmberSource: true,
    skipBabel: [
      {
        package: 'qunit',
      },
    ],
    webpackConfig: {
      watchOptions: {
        ignored: /node_modules/,
      },
    },
    'ember-simple-auth': {
      useSessionSetupMethod: true,
    },
  });
};
