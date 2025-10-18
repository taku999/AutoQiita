import * as vscode from 'vscode';
import axios from 'axios';

interface MCPResponse {
    result?: any;
    error?: string;
}

export class AutoQiitaClient {
    private baseUrl: string;
    private isMonitoring: boolean = false;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    async initialize(workspacePath: string): Promise<MCPResponse> {
        try {
            const response = await axios.post(`${this.baseUrl}/mcp/request`, {
                method: 'initialize',
                params: { workspace_path: workspacePath }
            });
            return response.data;
        } catch (error) {
            return { error: `Failed to initialize: ${error}` };
        }
    }

    async startMonitoring(): Promise<MCPResponse> {
        try {
            const response = await axios.post(`${this.baseUrl}/mcp/request`, {
                method: 'start_monitoring',
                params: {}
            });
            if (!response.data.error) {
                this.isMonitoring = true;
            }
            return response.data;
        } catch (error) {
            return { error: `Failed to start monitoring: ${error}` };
        }
    }

    async stopMonitoring(): Promise<MCPResponse> {
        try {
            const response = await axios.post(`${this.baseUrl}/mcp/request`, {
                method: 'stop_monitoring',
                params: {}
            });
            if (!response.data.error) {
                this.isMonitoring = false;
            }
            return response.data;
        } catch (error) {
            return { error: `Failed to stop monitoring: ${error}` };
        }
    }

    async saveToQiita(filePath: string): Promise<MCPResponse> {
        try {
            const response = await axios.post(`${this.baseUrl}/mcp/request`, {
                method: 'save_to_qiita',
                params: { file_path: filePath }
            });
            return response.data;
        } catch (error) {
            return { error: `Failed to save to Qiita: ${error}` };
        }
    }

    async getStatus(): Promise<MCPResponse> {
        try {
            const response = await axios.post(`${this.baseUrl}/mcp/request`, {
                method: 'get_status',
                params: {}
            });
            return response.data;
        } catch (error) {
            return { error: `Failed to get status: ${error}` };
        }
    }

    async checkHealth(): Promise<boolean> {
        try {
            const response = await axios.get(`${this.baseUrl}/health`, { timeout: 5000 });
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }

    getMonitoringStatus(): boolean {
        return this.isMonitoring;
    }
}