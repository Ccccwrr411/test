module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.js', '**/?(*.)+(spec|test).js'],
  transformIgnorePatterns: ['/node_modules/(?!@opentelemetry)'],
};
