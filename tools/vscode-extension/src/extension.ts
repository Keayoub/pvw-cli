import * as vscode from 'vscode';
import * as path from 'path';
import { execSync, exec, spawn } from 'child_process';
import * as fs from 'fs';

let mcpTerminal: vscode.Terminal | undefined;
let logTailTimer: NodeJS.Timeout | undefined;
let logLastSize = 0;

interface DiagnosticResult {
    success: boolean;
    errors: string[];
    warnings: string[];
    passed: string[];
    recommendations: string[];
}

async function installPythonDependencies(extensionPath: string, outputChannel: vscode.OutputChannel): Promise<boolean> {
    const requirementsPath = path.join(extensionPath, 'bundled', 'requirements.txt');

    outputChannel.appendLine('Installing Python dependencies...');
    outputChannel.appendLine(`Requirements file: ${requirementsPath}`);

    try {
        const output = execSync(`pip install -r "${requirementsPath}"`, {
            encoding: 'utf8',
            timeout: 120000, // 2 minutes timeout
            stdio: 'pipe'
        });
        outputChannel.appendLine(output);
        outputChannel.appendLine('✓ Dependencies installed successfully');
        return true;
    } catch (e: any) {
        outputChannel.appendLine('✗ Failed to install dependencies:');
        outputChannel.appendLine(e.message || String(e));
        return false;
    }
}

async function runDiagnostics(repoRoot: string, pythonPath: string, requirementsPath: string): Promise<DiagnosticResult> {
    const result: DiagnosticResult = {
        success: true,
        errors: [],
        warnings: [],
        passed: [],
        recommendations: []
    };

    // Check 1: Verify server.py exists
    try {
        await vscode.workspace.fs.stat(vscode.Uri.file(pythonPath));
        result.passed.push('✓ server.py found');
    } catch (e) {
        result.errors.push('server.py not found at: ' + pythonPath);
        result.success = false;
        return result;
    }

    // Check 2: Verify Python is available
    try {
        const pythonVersion = execSync('python --version', { encoding: 'utf8', timeout: 5000 }).trim();
        result.passed.push(`✓ Python available: ${pythonVersion}`);
    } catch (e) {
        result.errors.push('Python not found. Install Python or activate your virtual environment');
        result.recommendations.push('Run: python --version to verify Python installation');
        result.success = false;
        return result;
    }

    // Check 3: Verify mcp package is installed
    try {
        execSync('python -c "import mcp"', { encoding: 'utf8', timeout: 5000, stdio: 'pipe' });
        result.passed.push('✓ mcp package installed');
    } catch (e) {
        result.errors.push('mcp package not installed');
        result.recommendations.push(`Run: pip install -r "${requirementsPath}"`);
        result.success = false;
    }

    // Check 3b: Verify fastmcp package is installed (new in v2.0)
    try {
        execSync('python -c "import fastmcp"', { encoding: 'utf8', timeout: 5000, stdio: 'pipe' });
        result.passed.push('✓ fastmcp package installed (v2.0 FastMCP server)');
    } catch (e) {
        // fastmcp is required now (no legacy support)
        result.errors.push('fastmcp package not installed (FastMCP is required)');
        result.recommendations.push(`Run: pip install fastmcp>=0.2.0`);
        result.success = false;
        return result;
    }

    // Check 4: Verify azure-identity package
    try {
        execSync('python -c "import azure.identity"', { encoding: 'utf8', timeout: 5000, stdio: 'pipe' });
        result.passed.push('✓ azure-identity package installed');
    } catch (e) {
        result.errors.push('azure-identity package not installed');
        result.recommendations.push(`Run: pip install -r "${requirementsPath}"`);
        result.success = false;
    }

    // Check 5: Verify purviewcli package (local package)
    try {
        // Set PYTHONPATH to include the repo root to find purviewcli
        const env = Object.assign({}, process.env, { PYTHONPATH: repoRoot });
        execSync('python -c "from purviewcli.client.api_client import PurviewClient"', {
            encoding: 'utf8',
            timeout: 5000,
            stdio: 'pipe',
            cwd: repoRoot,
            env: env
        });
        result.passed.push('✓ purviewcli package available');
    } catch (e) {
        // This is just a warning since the server might still work
        result.warnings.push('purviewcli package check failed (non-critical)');
        result.recommendations.push(`Optional: Run "pip install -e ." from ${repoRoot} to install purviewcli in editable mode`);
    }

    // Check 6: Verify Azure authentication
    try {
        execSync('az account show', { encoding: 'utf8', timeout: 5000, stdio: 'pipe' });
        result.passed.push('✓ Azure CLI authenticated');
    } catch (e) {
        result.warnings.push('Azure CLI not authenticated');
        result.recommendations.push('Run: az login');
    }

    // Check 7: Verify requirements.txt exists
    try {
        await vscode.workspace.fs.stat(vscode.Uri.file(requirementsPath));
        result.passed.push('✓ requirements.txt found');
    } catch (e) {
        result.warnings.push('requirements.txt not found');
    }

    return result;
}

export function activate(context: vscode.ExtensionContext) {
    console.log('Purview MCP Server extension activated');

    const outputChannel = vscode.window.createOutputChannel('Purview MCP Server');
    context.subscriptions.push(outputChannel);

    outputChannel.appendLine('Purview MCP Server extension activated');
    outputChannel.appendLine('GitHub Copilot will automatically start the MCP server when needed');
    outputChannel.appendLine('Use "Purview MCP: Diagnose Setup" to verify configuration');

    // Optionally auto-install Python dependencies if user enabled it
    try {
        const config = vscode.workspace.getConfiguration('purview-mcp');
        const autoInstall = config.get<boolean>('autoInstallDependencies', false);
        if (autoInstall) {
            (async () => {
                // If developmentMode is enabled, perform the install without prompting (developer convenience)
                const devMode = config.get<boolean>('developmentMode', false);
                if (devMode) {
                    outputChannel.show();
                    const installed = await installPythonDependencies(context.extensionPath, outputChannel);
                    if (!installed) {
                        vscode.window.showErrorMessage('Auto-install failed (development mode). Check Purview MCP Server output for details.');
                    } else {
                        vscode.window.showInformationMessage('Python dependencies installed successfully (development mode)');
                    }
                    return;
                }

                // Otherwise ask for confirmation before installing
                    outputChannel.appendLine('Auto-install enabled: installing Python dependencies from bundled/requirements.txt');
                    outputChannel.show();
                    const installed = await installPythonDependencies(context.extensionPath, outputChannel);
                    if (!installed) {
                        vscode.window.showErrorMessage('Auto-install failed. Check Purview MCP Server output for details.');
                    } else {
                        vscode.window.showInformationMessage('Python dependencies installed successfully');
                    }
            })();
        }
    } catch (e) {
        // ignore errors during optional auto-install
    }

    const startCmd = vscode.commands.registerCommand('purview-mcp.startServer', async () => {
        // Use bundled server.py from extension
        const serverPath = path.join(context.extensionPath, 'bundled', 'server.py');
        const requirementsPath = path.join(context.extensionPath, 'bundled', 'requirements.txt');

        // Check if server is already running
        if (mcpTerminal && mcpTerminal.exitStatus === undefined) {
            vscode.window.showInformationMessage('Purview MCP Server is already running');
            mcpTerminal.show(false);
            return;
        }

        const config = vscode.workspace.getConfiguration('purview-mcp');
        let accountName = config.get<string>('accountName');
        let accountId = config.get<string>('accountId');
        let tenantId = config.get<string>('tenantId');
        const developmentMode = config.get<boolean>('developmentMode', false);

        // Prompt for account if not configured
        if (!accountName || accountName.trim() === '') {
            accountName = await vscode.window.showInputBox({
                prompt: 'Enter your Purview account name',
                placeHolder: 'your-purview-account',
                ignoreFocusOut: true
            });

            if (!accountName) {
                vscode.window.showErrorMessage('PURVIEW_ACCOUNT_NAME is required to start the MCP server');
                return;
            }

            // Offer to save it
            const save = await vscode.window.showQuickPick(['Yes', 'No'], {
                placeHolder: 'Save account name to workspace settings?'
            });
            if (save === 'Yes') {
                await config.update('accountName', accountName, vscode.ConfigurationTarget.Workspace);
            }
        }

        // Optionally prompt for account ID (for Unified Catalog)
        if (!accountId || accountId.trim() === '') {
            const promptAccountId = await vscode.window.showQuickPick(['Skip', 'Enter account ID'], {
                placeHolder: 'Purview Account ID (optional, for Unified Catalog)'
            });

            if (promptAccountId === 'Enter account ID') {
                accountId = await vscode.window.showInputBox({
                    prompt: 'Enter your Purview account ID (optional)',
                    placeHolder: 'account-id',
                    ignoreFocusOut: true
                });

                if (accountId) {
                    const save = await vscode.window.showQuickPick(['Yes', 'No'], {
                        placeHolder: 'Save account ID to workspace settings?'
                    });
                    if (save === 'Yes') {
                        await config.update('accountId', accountId, vscode.ConfigurationTarget.Workspace);
                    }
                }
            }
        }

        // Optionally prompt for tenant
        if (!tenantId || tenantId.trim() === '') {
            const promptTenant = await vscode.window.showQuickPick(['Skip', 'Enter tenant ID'], {
                placeHolder: 'Azure Tenant ID (optional, press Enter to skip)'
            });

            if (promptTenant === 'Enter tenant ID') {
                tenantId = await vscode.window.showInputBox({
                    prompt: 'Enter your Azure tenant ID (optional)',
                    placeHolder: 'tenant-id',
                    ignoreFocusOut: true
                });

                if (tenantId) {
                    const save = await vscode.window.showQuickPick(['Yes', 'No'], {
                        placeHolder: 'Save tenant ID to workspace settings?'
                    });
                    if (save === 'Yes') {
                        await config.update('tenantId', tenantId, vscode.ConfigurationTarget.Workspace);
                    }
                }
            }
        }

        // Run diagnostics before starting
        const diagnostics = await runDiagnostics(context.extensionPath, serverPath, requirementsPath);

        if (!diagnostics.success) {
            const action = await vscode.window.showErrorMessage(
                `Setup incomplete: ${diagnostics.errors.join(', ')}`,
                'Show Details',
                'Continue Anyway'
            );

            if (action === 'Show Details') {
                const outputChannel = vscode.window.createOutputChannel('Purview MCP Diagnostics');
                outputChannel.clear();
                outputChannel.appendLine('=== Purview MCP Server Diagnostics ===\n');
                outputChannel.appendLine('❌ Errors:');
                diagnostics.errors.forEach(err => outputChannel.appendLine(`  - ${err}`));

                if (diagnostics.warnings.length > 0) {
                    outputChannel.appendLine('\n⚠️  Warnings:');
                    diagnostics.warnings.forEach(warn => outputChannel.appendLine(`  - ${warn}`));
                }

                outputChannel.appendLine('\n✅ Checks Passed:');
                diagnostics.passed.forEach(pass => outputChannel.appendLine(`  - ${pass}`));

                outputChannel.appendLine('\n📋 Recommended Actions:');
                diagnostics.recommendations.forEach(rec => outputChannel.appendLine(`  - ${rec}`));

                outputChannel.show();
                return;
            } else if (action !== 'Continue Anyway') {
                return;
            }
        } else if (diagnostics.warnings.length > 0) {
            const action = await vscode.window.showWarningMessage(
                `${diagnostics.warnings.length} warning(s) detected. Continue?`,
                'Show Details',
                'Continue'
            );

            if (action === 'Show Details') {
                const outputChannel = vscode.window.createOutputChannel('Purview MCP Diagnostics');
                outputChannel.clear();
                outputChannel.appendLine('=== Purview MCP Server Diagnostics ===\n');
                outputChannel.appendLine('⚠️  Warnings:');
                diagnostics.warnings.forEach(warn => outputChannel.appendLine(`  - ${warn}`));

                outputChannel.appendLine('\n✅ Checks Passed:');
                diagnostics.passed.forEach(pass => outputChannel.appendLine(`  - ${pass}`));

                outputChannel.show();
                return;
            }
        }

        // Create terminal with environment variables
        const env: { [key: string]: string } = {
            PURVIEW_ACCOUNT_NAME: accountName
        };

        if (accountId && accountId.trim() !== '') {
            env.PURVIEW_ACCOUNT_ID = accountId;
        }

        if (tenantId && tenantId.trim() !== '') {
            env.AZURE_TENANT_ID = tenantId;
        }

        // Check if dependencies need to be installed
        try {
            execSync('python -c "import mcp"', { encoding: 'utf8', timeout: 5000, stdio: 'pipe' });
        } catch (e) {
            const installDeps = await vscode.window.showInformationMessage(
                'Python dependencies not found. Install them now?',
                'Yes', 'No'
            );

            if (installDeps === 'Yes') {
                outputChannel.show();
                const installed = await installPythonDependencies(context.extensionPath, outputChannel);
                if (!installed) {
                    vscode.window.showErrorMessage('Failed to install dependencies. Check output for details.');
                    return;
                }
            } else {
                vscode.window.showErrorMessage('Cannot start server without dependencies.');
                return;
            }
        }

        // Start the server directly with python
        // Offer choices: let Copilot/VS Code manage the MCP server, or start a
        // detached background process (no visible terminal). Recommended: let
        // Copilot start the server so it can manage lifecycle and stdio.
        const pick = await vscode.window.showQuickPick([
            'Let Copilot/VS Code manage the MCP server (recommended)',
            'Start background server process (detached, no terminal)'
        ], { placeHolder: 'How would you like to start the Purview MCP server?' });

        if (!pick) {
            return; // user cancelled
        }

    // determine repo root (if available)
    const workspaceFolders = vscode.workspace.workspaceFolders;
    const repoRoot = workspaceFolders && workspaceFolders.length > 0 ? workspaceFolders[0].uri.fsPath : undefined;

    if (pick.startsWith('Start background')) {
            try {
                // spawn a detached python process so it runs in background without a terminal
                const child = spawn('python', [serverPath, '--no-banner'], {
                    detached: true,
                    stdio: 'ignore',
                    env: Object.assign({}, process.env, env),
                    cwd: repoRoot || undefined
                });
                child.unref();
                outputChannel.show(true);
                outputChannel.appendLine(`Started Purview MCP Server as detached process (PID ${child.pid})`);
                const modeMessage = developmentMode ? ' (Development Mode)' : '';
                vscode.window.showInformationMessage(`Purview MCP Server started in background${modeMessage}`);
            } catch (err: any) {
                outputChannel.appendLine('Failed to start background MCP server: ' + (err.message || String(err)));
                vscode.window.showErrorMessage('Failed to start MCP server in background. See output for details.');
            }
        } else {
            vscode.window.showInformationMessage('To let Copilot/VS Code manage the MCP server, open the MCP servers list in the Extensions/Model Context Protocol area and start the server from there.');
        }
    });

    const stopCmd = vscode.commands.registerCommand('purview-mcp.stopServer', () => {
        if (mcpTerminal) {
            mcpTerminal.dispose();
            mcpTerminal = undefined;
            if (logTailTimer) {
                clearInterval(logTailTimer);
                logTailTimer = undefined;
            }
            vscode.window.showInformationMessage('Purview MCP Server stopped');
        } else {
            vscode.window.showWarningMessage('No MCP server terminal found');
        }
    });

    const diagnoseCmd = vscode.commands.registerCommand('purview-mcp.diagnose', async () => {
        const bundledServerPath = path.join(context.extensionPath, 'bundled', 'server.py');
        const bundledRequirementsPath = path.join(context.extensionPath, 'bundled', 'requirements.txt');

        const diagOutputChannel = vscode.window.createOutputChannel('Purview MCP Diagnostics');
        diagOutputChannel.clear();
        diagOutputChannel.show();

        diagOutputChannel.appendLine('=== Purview MCP Server Diagnostics ===\n');
        diagOutputChannel.appendLine('Running diagnostics, please wait...\n');

        const diagnostics = await runDiagnostics(context.extensionPath, bundledServerPath, bundledRequirementsPath);

        if (diagnostics.errors.length > 0) {
            diagOutputChannel.appendLine('❌ ERRORS:\n');
            diagnostics.errors.forEach(err => diagOutputChannel.appendLine(`  ${err}`));
            diagOutputChannel.appendLine('');
        }

        if (diagnostics.warnings.length > 0) {
            diagOutputChannel.appendLine('⚠️  WARNINGS:\n');
            diagnostics.warnings.forEach(warn => diagOutputChannel.appendLine(`  ${warn}`));
            diagOutputChannel.appendLine('');
        }

        if (diagnostics.passed.length > 0) {
            diagOutputChannel.appendLine('✅ PASSED:\n');
            diagnostics.passed.forEach(pass => diagOutputChannel.appendLine(`  ${pass}`));
            diagOutputChannel.appendLine('');
        }

        if (diagnostics.recommendations.length > 0) {
            diagOutputChannel.appendLine('📋 RECOMMENDED ACTIONS:\n');
            diagnostics.recommendations.forEach(rec => diagOutputChannel.appendLine(`  ${rec}`));
            diagOutputChannel.appendLine('');
        }

        diagOutputChannel.appendLine('═══════════════════════════════════\n');

        if (diagnostics.success) {
            diagOutputChannel.appendLine('✅ All checks passed! Ready to start the MCP server.');
            vscode.window.showInformationMessage('Diagnostics passed! Ready to start the MCP server.');
        } else {
            diagOutputChannel.appendLine('❌ Setup incomplete. Please fix the errors above.');
            vscode.window.showErrorMessage(`Diagnostics failed: ${diagnostics.errors.length} error(s) found. Check the output for details.`);
        }
    });

    context.subscriptions.push(startCmd, stopCmd, diagnoseCmd);
}

export function deactivate() {
    if (mcpTerminal) {
        mcpTerminal.dispose();
    }
}
