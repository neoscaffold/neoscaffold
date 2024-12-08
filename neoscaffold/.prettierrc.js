'use strict';

module.exports = {
  overrides: [
    {
      files: '*.{js,ts}',
      options: {
        singleQuote: true,
        useTabs: false,
        tabWidth: 2,
      },
    },
    {
      files: '*.{html,hbs}',
      options: {
        parser: 'glimmer',
        htmlWhitespaceSensitivity: 'strict',
        singleQuote: false,
        bracketSameLine: true,
        singleAttributePerLine: false,
        useTabs: false,
        tabWidth: 2,
      },
    },
  ],
};
