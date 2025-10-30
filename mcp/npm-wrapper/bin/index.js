#!/usr/bin/env node
const execa = require('execa');
const argv = require('minimist')(process.argv.slice(2));

async function main() {
  const account = argv.account || process.env.PURVIEW_ACCOUNT_NAME;
  const tenant = argv.tenant || process.env.AZURE_TENANT_ID;
  const image = argv.image || process.env.PURVIEW_MCP_IMAGE || 'purview-mcp:latest';

  if (!account) {
    console.error('PURVIEW_ACCOUNT_NAME required. Pass --account or set PURVIEW_ACCOUNT_NAME');
    process.exit(1);
  }

  const envArgs = [
    '-e', `PURVIEW_ACCOUNT_NAME=${account}`
  ];
  if (tenant) envArgs.push('-e', `AZURE_TENANT_ID=${tenant}`);

  // Mount current repo parent into /app in container if running from mcp folder
  const cwd = process.cwd();
  const mount = `${cwd}/..:/app:rw`;

  const dockerArgs = ['run', '--rm', '-i', ...envArgs, '-v', mount, image];

  try {
    const child = execa('docker', dockerArgs, { stdio: 'inherit' });
    await child;
  } catch (err) {
    console.error('Failed to run docker container:', err.message);
    process.exit(1);
  }
}

main();
