// API_BASE_URL 现在由 config.js 管理，不再在此处声明

const api = {
    /**
     * 检查后端健康状态
     */
    async checkHealth() {
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/health`);
        if (!response.ok) throw new Error('网络响应错误');
        return response.json();
    },

    /**
     * 解析文档
     * @param {FormData} formData 包含文件的表单数据
     * @param {URLSearchParams} params 查询参数
     */
    async parseDocument(formData, params) {
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/parser/parse?${params.toString()}`, {
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
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/tender/generate?${params.toString()}`, {
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
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/tender/status/${taskId}`);
        if (!response.ok) throw new Error('获取任务状态失败');
        return response.json();
    },

    /**
     * 获取历史记录 (支持分页)
     * @param {URLSearchParams} params 查询参数 (分页等)
     */
    async getHistory(params) {
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/history/records?${params.toString()}`);
        if (!response.ok) throw new Error('获取历史记录失败');
        return response.json();
    },

    /**
     * 删除一条历史记录
     * @param {string} recordId 记录ID
     */
    async deleteHistoryRecord(recordId) {
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/history/records/${recordId}`, {
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
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/history/export/${recordId}`);
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
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/filter/process`, {
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
    },

    /**
     * 从JSON数据生成投标书
     * @param {Object} jsonData JSON数据
     * @param {boolean} enableOptimization 是否启用优化
     * @param {boolean} includeAnalysis 是否包含分析
     * @param {string} modelName 模型名称
     */
    async generateBidProposalFromJSON(jsonData, enableOptimization = true, includeAnalysis = true, modelName = null) {
        const requestBody = {
            tender_document_json: jsonData,
            generate_outline_only: false
        };
        
        if (modelName) {
            requestBody.model_name = modelName;
        }
        
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/gender_book/generate_from_json`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '投标书生成失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    },

    /**
     * 从文件生成投标书
     * @param {FormData} formData 包含文件和选项的表单数据
     */
    async generateBidProposalFromFile(formData) {
        // 创建AbortController用于超时控制
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60秒超时
        
        try {
            const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
            const response = await fetch(`${baseUrl}/api/gender_book/upload_json`, {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: '投标书生成失败' }));
                throw new Error(errorData.detail);
            }
            return response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('请求超时，任务创建可能需要更长时间，请稍后查看任务状态');
            }
            throw error;
        }
    },

    /**
     * 查询投标书生成任务状态
     * @param {string} taskId 任务ID
     */
    async getBidProposalTaskStatus(taskId) {
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/gender_book/status/${taskId}`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '获取任务状态失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    },

    /**
     * 获取所有投标书生成任务状态
     */
    async getAllBidProposalTasks() {
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/gender_book/tasks`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '获取任务列表失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    },

    /**
     * 删除投标书生成任务
     * @param {string} taskId 任务ID
     */
    async deleteBidProposalTask(taskId) {
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/gender_book/tasks/${taskId}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '删除任务失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    },

    /**
     * 分析招标文件JSON内容
     * @param {Object} jsonData JSON数据
     * @param {string} modelName 模型名称
     */
    async analyzeTenderDocumentContent(jsonData, modelName = null) {
        const requestBody = { tender_document_json: jsonData };
        
        if (modelName) {
            requestBody.model_name = modelName;
        }
        
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/gender_book/analyze_json`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '内容分析失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    },

    /**
     * 检查投标书生成服务健康状态
     */
    async checkBidProposalHealth() {
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/gender_book/health`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '健康检查失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    },

    /**
     * 获取标准章节模板
     */
    async getStandardSections() {
        const baseUrl = window.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/gender_book/sections`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '获取标准章节失败' }));
            throw new Error(errorData.detail);
        }
        return response.json();
    }
};