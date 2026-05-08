#!/usr/bin/env node

/*
 * npx entrypoint for the Purview MCP server.
 *
 * Priority order:
 * 1) Existing pvw-mcp executable in PATH
 * 2) uvx runner (recommended)
 *
 * Set PVW_MCP_UV_FROM to override uvx source, for example:
 * - pvw-mcp-server
 * - git+https://github.com/Keayoub/pvw-cli.git#subdirectory=tools/PurviewMCPServer
 */

const { spawn, spawnSync } = require("child_process");

const DEFAULT_UV_FROM =
  "git+https://github.com/Keayoub/pvw-cli.git#subdirectory=tools/PurviewMCPServer";

function run(command, args) {
  const child = spawn(command, args, {
    stdio: "inherit",
    shell: process.platform === "win32",
    env: process.env,
  });

  child.on("error", (err) => {
    if (err && err.code === "ENOENT") {
      process.exit(127);
      return;
    }
    process.stderr.write(`[X] Failed to start '${command}': ${err.message}\n`);
    process.exit(1);
  });

  child.on("exit", (code, signal) => {
    if (signal) {
      process.stderr.write(`[X] Process terminated by signal: ${signal}\n`);
      process.exit(1);
      return;
    }
    process.exit(code || 0);
  });
}

function exists(command) {
  const probeArgs = process.platform === "win32" ? ["--version"] : ["--help"];
  const result = spawnSync(command, probeArgs, {
    stdio: "ignore",
    shell: process.platform === "win32",
    env: process.env,
  });
  return !result.error;
}

const userArgs = process.argv.slice(2);

// If pvw-mcp is already available, use it directly.
if (process.env.PVW_MCP_NO_DIRECT !== "1" && exists("pvw-mcp")) {
  run("pvw-mcp", userArgs);
} else if (exists("uvx")) {
  // Otherwise, run through uvx using a configurable source.
  const uvFrom = process.env.PVW_MCP_UV_FROM || DEFAULT_UV_FROM;
  const uvxArgs = ["--from", uvFrom, "pvw-mcp", ...userArgs];
  run("uvx", uvxArgs);
} else {
  process.stderr.write(
    "[X] Could not find 'pvw-mcp' or 'uvx'. Install uv (https://docs.astral.sh/uv/) or install the Python package first.\n"
  );
  process.exit(127);
}
