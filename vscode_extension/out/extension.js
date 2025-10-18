"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const autoqiitaClient_1 = require("./autoqiitaClient");
let client;
let statusBarItem;
function activate(context) {
    console.log('AutoQiita extension is now active!');
    // Get configuration
    const config = vscode.workspace.getConfiguration('autoqiita');
    const mcpServerUrl = config.get('mcpServerUrl', 'http://localhost:8000');
    // Initialize client
    client = new autoqiitaClient_1.AutoQiitaClient(mcpServerUrl);
    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'autoqiita.showStatus';
    updateStatusBarItem('Disconnected');
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    // Register commands
    const startMonitoringCommand = vscode.commands.registerCommand('autoqiita.startMonitoring', startMonitoring);
    const stopMonitoringCommand = vscode.commands.registerCommand('autoqiita.stopMonitoring', stopMonitoring);
    const saveCurrentFileCommand = vscode.commands.registerCommand('autoqiita.saveCurrentFile', saveCurrentFile);
    const showStatusCommand = vscode.commands.registerCommand('autoqiita.showStatus', showStatus);
    context.subscriptions.push(startMonitoringCommand, stopMonitoringCommand, saveCurrentFileCommand, showStatusCommand);
    // Initialize connection
    initializeConnection();
    // Auto-start monitoring if enabled
    const autoSaveEnabled = config.get('autoSaveEnabled', true);
    if (autoSaveEnabled) {
        setTimeout(() => {
            startMonitoring();
        }, 2000); // Wait 2 seconds for server to be ready
    }
}
exports.activate = activate;
async function initializeConnection() {
    try {
        // Check if server is healthy
        const isHealthy = await client.checkHealth();
        if (!isHealthy) {
            vscode.window.showWarningMessage('AutoQiita MCP server is not responding. Please start the server.');
            updateStatusBarItem('Server Offline');
            return;
        }
        // Get workspace path
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder found. Please open a workspace.');
            return;
        }
        const workspacePath = workspaceFolders[0].uri.fsPath;
        // Initialize MCP connection
        const result = await client.initialize(workspacePath);
        if (result.error) {
            vscode.window.showErrorMessage(`Failed to initialize AutoQiita: ${result.error}`);
            updateStatusBarItem('Error');
        }
        else {
            updateStatusBarItem('Ready');
            console.log('AutoQiita initialized successfully');
        }
    }
    catch (error) {
        console.error('Failed to initialize AutoQiita:', error);
        updateStatusBarItem('Error');
    }
}
async function startMonitoring() {
    try {
        updateStatusBarItem('Starting...');
        const result = await client.startMonitoring();
        if (result.error) {
            vscode.window.showErrorMessage(`Failed to start monitoring: ${result.error}`);
            updateStatusBarItem('Error');
        }
        else {
            updateStatusBarItem('Monitoring');
            vscode.window.showInformationMessage('AutoQiita monitoring started');
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`Error starting monitoring: ${error}`);
        updateStatusBarItem('Error');
    }
}
async function stopMonitoring() {
    try {
        updateStatusBarItem('Stopping...');
        const result = await client.stopMonitoring();
        if (result.error) {
            vscode.window.showErrorMessage(`Failed to stop monitoring: ${result.error}`);
        }
        else {
            updateStatusBarItem('Ready');
            vscode.window.showInformationMessage('AutoQiita monitoring stopped');
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`Error stopping monitoring: ${error}`);
        updateStatusBarItem('Error');
    }
}
async function saveCurrentFile() {
    try {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
            vscode.window.showWarningMessage('No active file to save');
            return;
        }
        const filePath = activeEditor.document.uri.fsPath;
        // Save file first
        await activeEditor.document.save();
        vscode.window.showInformationMessage('Saving to Qiita...');
        const result = await client.saveToQiita(filePath);
        if (result.error) {
            vscode.window.showErrorMessage(`Failed to save to Qiita: ${result.error}`);
        }
        else {
            const title = result.result?.title || 'Unknown';
            const url = result.result?.url;
            if (url) {
                const action = await vscode.window.showInformationMessage(`Saved "${title}" to Qiita`, 'Open in Browser');
                if (action === 'Open in Browser') {
                    vscode.env.openExternal(vscode.Uri.parse(url));
                }
            }
            else {
                vscode.window.showInformationMessage(`Saved "${title}" to Qiita`);
            }
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`Error saving file: ${error}`);
    }
}
async function showStatus() {
    try {
        const result = await client.getStatus();
        if (result.error) {
            vscode.window.showErrorMessage(`Failed to get status: ${result.error}`);
            return;
        }
        const status = result.result;
        const monitoring = status?.monitoring ? 'Active' : 'Inactive';
        const workspacePath = status?.workspace_path || 'Unknown';
        const extensions = status?.watched_extensions?.join(', ') || 'Unknown';
        const message = `AutoQiita Status:
Monitoring: ${monitoring}
Workspace: ${workspacePath}
Watched Extensions: ${extensions}`;
        vscode.window.showInformationMessage(message);
    }
    catch (error) {
        vscode.window.showErrorMessage(`Error getting status: ${error}`);
    }
}
function updateStatusBarItem(status) {
    statusBarItem.text = `$(sync) AutoQiita: ${status}`;
    switch (status) {
        case 'Monitoring':
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.activeBackground');
            break;
        case 'Error':
        case 'Server Offline':
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            break;
        default:
            statusBarItem.backgroundColor = undefined;
            break;
    }
}
function deactivate() {
    if (client && client.getMonitoringStatus()) {
        client.stopMonitoring();
    }
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map