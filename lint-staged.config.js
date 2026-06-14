process.env.ESLINT_USE_FLAT_CONFIG = 'true';

module.exports = {
  // Only lint workspace packages
  'packages/*/*.{js,cjs,ts,tsx}': 'eslint --fix --max-warnings=0',
  'packages/**/*.{json,md}': 'prettier --write',
  'packages/**/tsconfig.base.json': 'prettier --write'
};
