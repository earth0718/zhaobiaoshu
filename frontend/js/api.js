const API_BASE_URL = 'http://localhost:8082'; // 在main.py中配置的端口

const api = {
    /**
     * 检查后端健康状态
     */
    async checkHealth() {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) throw new Error('网络响应错误');
        return response.json();
    },

    /**
     * 解析文档
     * @param {FormData} formData 包含文件的表单数据
     * @param {URLSearchParams} params 查询参数
     */
    async parseDocument(formData, params) {
        const response = await fetch(`${API_BASE_URL}/api/parser/parse?${params.toString()}`, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '文档解析失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    },

    /**
     * 生成招标书
     * @param {FormData} formData 包含文件和选项的表单数据
     * @param {URLSearchParams} params 查询参数
     */
    async generateTender(formData, params) {
        const response = await fetch(`${API_BASE_URL}/api/tender/generate?${params.toString()}`, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '招标文件生成任务创建失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    },

    /**
     * 查询任务状态
     * @param {string} taskId 任务ID
     */
    async getTaskStatus(taskId) {
        const response = await fetch(`${API_BASE_URL}/api/tender/status/${taskId}`);
        if (!response.ok) throw new Error('获取任务状态失败');
        return response.json();
    },

    /**
     * 获取历史记录 (支持分页)
     * @param {URLSearchParams} params 查询参数 (分页等)
     */
    async getHistory(params) {
        const response = await fetch(`${API_BASE_URL}/api/history/records?${params.toString()}`);
        if (!response.ok) throw new Error('获取历史记录失败');
        return response.json();
    },

    /**
     * 删除一条历史记录
     * @param {string} recordId 记录ID
     */
    async deleteHistoryRecord(recordId) {
        const response = await fetch(`${API_BASE_URL}/api/history/records/${recordId}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '删除失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    },

    /**
     * 导出历史记录文件
     * @param {string} recordId 记录ID
     * @returns {Promise<Blob>}
     */
    async exportHistoryRecord(recordId) {
        const response = await fetch(`${API_BASE_URL}/api/history/export/${recordId}`);
        if (!response.ok) {
            throw new Error('导出失败');
        }
        return response.blob();
    },

    /**
     * 过滤JSON数据
     * @param {Object} jsonData 需要过滤的JSON数据
     */
    async filterJSON(jsonData) {
        const response = await fetch(`${API_BASE_URL}/api/filter/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'JSON过滤失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    }
};