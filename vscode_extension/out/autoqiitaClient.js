"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AutoQiitaClient = void 0;
const axios_1 = require("axios");
class AutoQiitaClient {
    constructor(baseUrl) {
        this.isMonitoring = false;
        this.baseUrl = baseUrl;
    }
    async initialize(workspacePath) {
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/mcp/request`, {
                method: 'initialize',
                params: { workspace_path: workspacePath }
            });
            return response.data;
        }
        catch (error) {
            return { error: `Failed to initialize: ${error}` };
        }
    }
    async startMonitoring() {
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/mcp/request`, {
                method: 'start_monitoring',
                params: {}
            });
            if (!response.data.error) {
                this.isMonitoring = true;
            }
            return response.data;
        }
        catch (error) {
            return { error: `Failed to start monitoring: ${error}` };
        }
    }
    async stopMonitoring() {
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/mcp/request`, {
                method: 'stop_monitoring',
                params: {}
            });
            if (!response.data.error) {
                this.isMonitoring = false;
            }
            return response.data;
        }
        catch (error) {
            return { error: `Failed to stop monitoring: ${error}` };
        }
    }
    async saveToQiita(filePath) {
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/mcp/request`, {
                method: 'save_to_qiita',
                params: { file_path: filePath }
            });
            return response.data;
        }
        catch (error) {
            return { error: `Failed to save to Qiita: ${error}` };
        }
    }
    async getStatus() {
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/mcp/request`, {
                method: 'get_status',
                params: {}
            });
            return response.data;
        }
        catch (error) {
            return { error: `Failed to get status: ${error}` };
        }
    }
    async checkHealth() {
        try {
            const response = await axios_1.default.get(`${this.baseUrl}/health`, { timeout: 5000 });
            return response.status === 200;
        }
        catch (error) {
            return false;
        }
    }
    getMonitoringStatus() {
        return this.isMonitoring;
    }
}
exports.AutoQiitaClient = AutoQiitaClient;
//# sourceMappingURL=autoqiitaClient.js.map