// 引入API基础URL常量
// 使用配置管理器获取API_BASE_URL，确保下载链接使用正确的基础URL
function getApiBaseUrl() {
    return window.configManager ? window.configManager.getApiBaseUrl() : (window.API_BASE_URL || 'http://localhost:8000');
}

class GenderBookGenerator {
    constructor(element) {
        this.element = element;
        this.currentTaskId = null;
        this.statusCheckInterval = null;
        this.render();
        this.attachEventListeners();
    }

    /**
     * 设置表单默认值，使用配置管理器获取默认配置
     */
    setDefaultValues() {
        if (window.configManager) {
            // 设置默认模型提供商
            const defaultProvider = window.configManager.getDefaultModelProvider();
            const providerSelect = this.element.querySelector('#gender-book-model-provider');
            if (providerSelect) {
                providerSelect.value = defaultProvider;
            }
            
            // 设置默认优化选项
            const defaultOptimization = window.configManager.getDefaultOptimizationSetting();
            const optimizationCheckbox = this.element.querySelector('#enable-optimization');
            if (optimizationCheckbox) {
                optimizationCheckbox.checked = defaultOptimization;
            }
            
            // 设置默认分析选项
            const defaultAnalysis = window.configManager.getDefaultAnalysisSetting();
            const analysisCheckbox = this.element.querySelector('#include-analysis');
            if (analysisCheckbox) {
                analysisCheckbox.checked = defaultAnalysis;
            }
        }
    }

    render() {
        this.element.innerHTML = `
            <div class="gender-book-container">
                <div class="upload-area form-group">
                    <label for="gender-book-file-input">选择JSON文件:</label>
                    <input type="file" id="gender-book-file-input" accept=".json">
                    <small class="help-text">请上传招标文件解析后生成的JSON文件</small>
                </div>
                
                <div class="attachment-upload-area form-group">
                    <label for="gender-book-attachments-input">上传附件 (可选):</label>
                    <input type="file" id="gender-book-attachments-input" multiple accept=".pdf,.jpg,.jpeg,.png,.doc,.docx">
                    <small class="help-text">支持PDF、图片和Word文档，可选择多个文件</small>
                    <div id="attachment-preview" class="attachment-preview"></div>
                </div>
                
                <div class="generation-options form-group">
                    <h3>生成选项</h3>
                    <div class="options-grid">
                        <div class="option-item">
                            <label for="gender-book-model-provider">模型提供商:</label>
                            <select id="gender-book-model-provider">
                                <option value="deepseek">DeepSeek (云端)</option>
                                <option value="ollama">Ollama (本地)</option>
                            </select>
                            <small>选择用于生成投标书的AI模型</small>
                        </div>
                        <div class="option-item">
                            <label>
                                <input type="checkbox" id="enable-optimization">
                                启用智能优化
                            </label>
                            <small>对小模型进行分章节优化处理</small>
                        </div>
                        <div class="option-item">
                            <label>
                                <input type="checkbox" id="include-analysis">
                                包含章节分析
                            </label>
                            <small>生成详细的章节结构分析</small>
                        </div>
                    </div>
                </div>

                <div class="generation-info form-group">
                    <h3>投标书生成功能说明</h3>
                    <ul>
                        <li>智能分析招标文件JSON内容，自动识别需求结构</li>
                        <li>针对小模型优化，分章节生成投标书内容</li>
                        <li>支持异步生成，可实时查看生成进度</li>
                        <li>提供标准投标章节模板和自定义章节支持</li>
                        <li>生成完整的投标书文档，支持多种格式输出</li>
                    </ul>
                </div>

                <div class="form-group">
                    <button id="gender-book-submit-btn" class="btn-primary">开始生成投标书</button>
                    <button id="gender-book-analyze-btn" class="btn-secondary">仅分析内容</button>
                </div>

                <div id="gender-book-result" class="result-area"></div>
            </div>
        `;
    }

    attachEventListeners() {
        const submitBtn = this.element.querySelector('#gender-book-submit-btn');
        const analyzeBtn = this.element.querySelector('#gender-book-analyze-btn');
        const attachmentsInput = this.element.querySelector('#gender-book-attachments-input');
        
        submitBtn.addEventListener('click', () => this.handleGeneration());
        analyzeBtn.addEventListener('click', () => this.handleAnalysis());
        attachmentsInput.addEventListener('change', () => this.handleAttachmentPreview());
        
        // 模型切换事件监听器
        this.element.querySelector('#gender-book-model-provider').addEventListener('change', (e) => {
            const modelProvider = e.target.value;
            const resultArea = this.element.querySelector('#gender-book-result');
            const modelName = modelProvider === 'deepseek' ? 'DeepSeek云端模型' : 'Ollama本地模型';
            ui.showMessage(resultArea, `已切换到${modelName}`, 'success');
        });
        
        // 设置默认值
        this.setDefaultValues();
    }

    async handleGeneration() {
        const fileInput = this.element.querySelector('#gender-book-file-input');
        const attachmentsInput = this.element.querySelector('#gender-book-attachments-input');
        const resultArea = this.element.querySelector('#gender-book-result');
        const modelProvider = this.element.querySelector('#gender-book-model-provider').value;
        const enableOptimization = this.element.querySelector('#enable-optimization').checked;
        const includeAnalysis = this.element.querySelector('#include-analysis').checked;

        if (fileInput.files.length === 0) {
            ui.showMessage(resultArea, '请先选择一个JSON文件。', 'error');
            return;
        }

        const file = fileInput.files[0];
        
        // 验证文件类型
        if (!file.name.toLowerCase().endsWith('.json')) {
            ui.showMessage(resultArea, '请选择有效的JSON文件。', 'error');
            return;
        }

        // 检查是否有附件
        const hasAttachments = attachmentsInput.files.length > 0;
        const attachmentText = hasAttachments ? `（包含${attachmentsInput.files.length}个附件）` : '';
        
        ui.showMessage(resultArea, `已切换到${modelProvider === 'deepseek' ? 'DeepSeek云端模型' : 'Ollama本地模型'}，正在创建生成任务${attachmentText}，请稍候...`, 'info');

        try {
            let result;
            
            if (hasAttachments) {
                // 如果有附件，使用新的API接口
                const jsonContent = await this.readFileAsText(file);
                const formData = new FormData();
                formData.append('tender_document_json', jsonContent);
                formData.append('model_name', modelProvider);
                formData.append('generate_outline_only', 'false');
                
                // 添加所有附件
                for (let i = 0; i < attachmentsInput.files.length; i++) {
                    formData.append('attachments', attachmentsInput.files[i]);
                }
                
                result = await api.generateBidProposalWithAttachments(formData);
            } else {
                // 没有附件，使用原有API接口
                const formData = new FormData();
                formData.append('file', file);
                formData.append('model_name', modelProvider);
                formData.append('generate_outline_only', 'false');
                
                result = await api.generateBidProposalFromFile(formData);
            }
            
            console.log('API返回结果:', result);
            
            // 检查result是否有task_id字段
            if (result && result.task_id && result.success) {
                this.currentTaskId = result.task_id;
                const taskData = {
                    task_id: result.task_id,
                    status: 'pending',
                    created_at: new Date().toISOString()
                };
                console.log('任务创建成功，task_id:', result.task_id);
                this.showTaskStatus(resultArea, taskData);
                this.startStatusPolling();
            } else {
                const errorMsg = result?.error || result?.message || '任务创建失败';
                ui.showMessage(resultArea, `生成失败: ${errorMsg}`, 'error');
                console.error('任务创建失败:', result);
            }
        } catch (error) {
            console.error('请求异常:', error);
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                ui.showMessage(resultArea, '网络连接失败，请检查后端服务是否正常运行', 'error');
            } else {
                ui.showMessage(resultArea, `请求失败: ${error.message}`, 'error');
            }
        }
    }

    async handleAnalysis() {
        const fileInput = this.element.querySelector('#gender-book-file-input');
        const resultArea = this.element.querySelector('#gender-book-result');
        const modelProvider = this.element.querySelector('#gender-book-model-provider').value;

        if (fileInput.files.length === 0) {
            ui.showMessage(resultArea, '请先选择一个JSON文件。', 'error');
            return;
        }

        const file = fileInput.files[0];
        
        // 验证文件类型
        if (!file.name.toLowerCase().endsWith('.json')) {
            ui.showMessage(resultArea, '请选择有效的JSON文件。', 'error');
            return;
        }

        ui.showMessage(resultArea, `已切换到${modelProvider === 'deepseek' ? 'DeepSeek云端模型' : 'Ollama本地模型'}，正在分析JSON内容，请稍候...`, 'info');

        try {
            // 读取文件内容
            const fileContent = await this.readFileAsText(file);
            
            // 验证JSON格式
            let jsonData;
            try {
                jsonData = JSON.parse(fileContent);
            } catch (parseError) {
                ui.showMessage(resultArea, '文件格式错误，请确保是有效的JSON文件。', 'error');
                return;
            }

            // 调用分析API，传递模型参数
            const result = await api.analyzeTenderDocumentContent(jsonData, modelProvider);
            
            if (result.success) {
                this.showAnalysisResult(resultArea, result.data, file.name);
            } else {
                ui.showMessage(resultArea, `分析失败: ${result.error || result.message}`, 'error');
            }
        } catch (error) {
            ui.showMessage(resultArea, `请求失败: ${error.message}`, 'error');
        }
    }

    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('文件读取失败'));
            reader.readAsText(file, 'UTF-8');
        });
    }

    showTaskStatus(resultArea, taskData) {
        const statusHtml = `
            <div class="task-status-container">
                <div class="task-info">
                    <h4>任务信息</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">任务ID:</span>
                            <span class="info-value">${taskData.task_id}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">状态:</span>
                            <span class="info-value status-${taskData.status}" id="task-status-text">${this.getStatusText(taskData.status)}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">创建时间:</span>
                            <span class="info-value">${new Date(taskData.created_at).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="btn-secondary" id="refresh-status-btn">
                        <i class="icon-refresh">🔄</i>
                        刷新状态
                    </button>
                    <button class="btn-danger" id="delete-task-btn">
                        <i class="icon-delete">🗑</i>
                        删除任务
                    </button>
                </div>
                <div id="task-progress" class="task-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 10%"></div>
                    </div>
                    <div class="progress-text">正在处理...</div>
                </div>
            </div>
        `;
        
        resultArea.innerHTML = statusHtml;
        
        // 缓存DOM元素引用以提高更新效率
        this.statusTextElement = resultArea.querySelector('#task-status-text');
        this.progressElement = resultArea.querySelector('#task-progress');
        this.progressFillElement = this.progressElement.querySelector('.progress-fill');
        this.progressTextElement = this.progressElement.querySelector('.progress-text');
        
        // 使用编程方式绑定事件处理器，而不是内联onclick
        const refreshBtn = resultArea.querySelector('#refresh-status-btn');
        const deleteBtn = resultArea.querySelector('#delete-task-btn');
        
        refreshBtn.addEventListener('click', () => {
            this.checkTaskStatus(taskData.task_id);
        });
        
        deleteBtn.addEventListener('click', () => {
            this.deleteTask(taskData.task_id);
        });
    }

    showAnalysisResult(resultArea, analysisData, fileName) {
        const { sections, statistics, recommendations } = analysisData;
        
        const analysisHtml = `
            <div class="analysis-container">
                <div class="success-message">
                    <i class="icon-success">✓</i>
                    <span>内容分析完成！</span>
                </div>
                
                <div class="analysis-stats">
                    <h4>分析统计</h4>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">文件名:</span>
                            <span class="stat-value">${fileName}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">识别章节数:</span>
                            <span class="stat-value">${statistics.total_sections}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">内容块数:</span>
                            <span class="stat-value">${statistics.total_content_blocks}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">总字符数:</span>
                            <span class="stat-value">${statistics.total_characters}</span>
                        </div>
                    </div>
                </div>

                <div class="sections-preview">
                    <h4>章节结构预览</h4>
                    <div class="sections-list">
                        ${sections.map((section, index) => `
                            <div class="section-item">
                                <div class="section-header">
                                    <span class="section-number">${index + 1}</span>
                                    <span class="section-title">${section.title}</span>
                                    <span class="section-confidence">置信度: ${(section.confidence * 100).toFixed(1)}%</span>
                                </div>
                                <div class="section-content">
                                    ${section.content.substring(0, 200)}${section.content.length > 200 ? '...' : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="recommendations">
                    <h4>生成建议</h4>
                    <ul>
                        ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>

                <div class="analysis-actions">
                    <button class="btn-primary" onclick="genderBookGenerator.proceedWithGeneration()">
                        <i class="icon-generate">📝</i>
                        基于此分析生成投标书
                    </button>
                </div>
            </div>
        `;
        
        resultArea.innerHTML = analysisHtml;
    }

    async startStatusPolling() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }

        // 使用配置管理器获取轮询间隔，提供更好的可配置性
        const pollingInterval = window.configManager ? window.configManager.getStatusPollingInterval() : 3000;
        this.statusCheckInterval = setInterval(async () => {
            if (this.currentTaskId) {
                await this.checkTaskStatus(this.currentTaskId);
            }
        }, pollingInterval);
    }

    async checkTaskStatus(taskId) {
        try {
            const result = await api.getBidProposalTaskStatus(taskId);
            
            if (result.success) {
                this.updateTaskStatus(result.data);
                
                // 如果任务完成，停止轮询
                if (result.data.status === 'completed' || result.data.status === 'failed') {
                    if (this.statusCheckInterval) {
                        clearInterval(this.statusCheckInterval);
                        this.statusCheckInterval = null;
                    }
                }
            }
        } catch (error) {
            console.error('检查任务状态失败:', error);
        }
    }

    updateTaskStatus(taskData) {
        // 使用缓存的DOM元素引用，提高更新效率
        if (this.statusTextElement) {
            this.statusTextElement.textContent = this.getStatusText(taskData.status);
            this.statusTextElement.className = `info-value status-${taskData.status}`;
        }

        if (this.progressElement && taskData.progress !== undefined) {
            if (this.progressFillElement) {
                this.progressFillElement.style.width = `${taskData.progress}%`;
            }
            
            if (this.progressTextElement) {
                this.progressTextElement.textContent = taskData.message || this.getStatusText(taskData.status);
            }
        }

        // 如果任务完成，显示结果
        if (taskData.status === 'completed' && taskData.result) {
            this.showCompletedResult(taskData);
        } else if (taskData.status === 'failed') {
            this.showFailedResult(taskData);
        }
    }

    showCompletedResult(taskData) {
        const resultArea = this.element.querySelector('#gender-book-result');
        const { result } = taskData;
        
        // 创建下载按钮HTML
        let downloadButtonsHtml = '';
        
        // Word格式下载按钮
        if (result.word_filename) {
            downloadButtonsHtml += `
                <button class="btn-download-primary" data-filename="${result.word_filename}" data-filetype="word">
                    <i class="icon-download">⬇</i>
                    下载Word文档
                </button>
            `;
        }
        
        // Markdown格式下载按钮
        if (result.markdown_filename) {
            downloadButtonsHtml += `
                <button class="btn-download-primary" data-filename="${result.markdown_filename}" data-filetype="markdown" style="margin-left: 10px;">
                    <i class="icon-download">⬇</i>
                    下载Markdown文档
                </button>
            `;
        }
        
        // 如果没有文件名，回退到原来的文本下载方式
        if (!result.word_filename && !result.markdown_filename) {
            let downloadUrl = '';
            let downloadFilename = '';
            
            if (result.docx_content) {
                const textContent = typeof result.docx_content === 'string' 
                    ? result.docx_content 
                    : new TextDecoder().decode(new Uint8Array(result.docx_content));
                
                const textBlob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
                downloadUrl = URL.createObjectURL(textBlob);
                downloadFilename = `投标书_${taskData.task_id}.txt`;
            } else if (result.bid_content) {
                const textBlob = new Blob([result.bid_content], { type: 'text/plain;charset=utf-8' });
                downloadUrl = URL.createObjectURL(textBlob);
                downloadFilename = `投标书_${taskData.task_id}.txt`;
            }
            
            if (downloadUrl) {
                downloadButtonsHtml = `
                    <a href="${downloadUrl}" download="${downloadFilename}" class="btn-download-primary">
                        <i class="icon-download">⬇</i>
                        下载投标书文档
                    </a>
                `;
                
                // 自动清理URL对象
                setTimeout(() => {
                    URL.revokeObjectURL(downloadUrl);
                }, 60000);
            }
        }
        
        const completedHtml = `
            <div class="completion-container">
                <div class="success-message">
                    <i class="icon-success">✓</i>
                    <span>投标书生成完成！</span>
                </div>
                
                <div class="download-section">
                    <h4>文档下载</h4>
                    <div class="download-info">
                        <p>投标书已成功生成，提供Word和Markdown两种格式下载。</p>
                        <div class="download-stats">
                            <span>任务ID: ${taskData.task_id}</span>
                            <span>完成时间: ${new Date(taskData.updated_at).toLocaleString()}</span>
                        </div>
                    </div>
                    <div class="download-actions">
                        ${downloadButtonsHtml}
                    </div>
                </div>
            </div>
        `;
        
        resultArea.innerHTML = completedHtml;
        
        // 为下载按钮绑定事件处理器
        const downloadButtons = resultArea.querySelectorAll('.btn-download-primary[data-filename]');
        downloadButtons.forEach(button => {
            button.addEventListener('click', () => {
                const fileName = button.getAttribute('data-filename');
                const fileType = button.getAttribute('data-filetype');
                this.downloadFile(fileName, fileType);
            });
        });
    }

    showFailedResult(taskData) {
        const resultArea = this.element.querySelector('#gender-book-result');
        
        const failedHtml = `
            <div class="failure-container">
                <div class="error-message">
                    <i class="icon-error">❌</i>
                    <span>投标书生成失败</span>
                </div>
                
                <div class="error-details">
                    <h4>错误信息</h4>
                    <p>${taskData.error || '未知错误'}</p>
                </div>

                <div class="failure-actions">
                    <button class="btn-primary" id="retry-generation-btn">
                        <i class="icon-retry">🔄</i>
                        重新生成
                    </button>
                    <button class="btn-danger" id="delete-failed-task-btn">
                        <i class="icon-delete">🗑</i>
                        删除任务
                    </button>
                </div>
            </div>
        `;
        
        resultArea.innerHTML = failedHtml;
        
        // 为失败页面的按钮绑定事件处理器
        const retryBtn = resultArea.querySelector('#retry-generation-btn');
        const deleteFailedBtn = resultArea.querySelector('#delete-failed-task-btn');
        
        retryBtn.addEventListener('click', () => {
            this.retryGeneration();
        });
        
        deleteFailedBtn.addEventListener('click', () => {
            this.deleteTask(taskData.task_id);
        });
    }

    async deleteTask(taskId) {
        if (!confirm('确定要删除这个任务吗？')) {
            return;
        }

        try {
            const result = await api.deleteBidProposalTask(taskId);
            
            if (result.success) {
                const resultArea = this.element.querySelector('#gender-book-result');
                ui.showMessage(resultArea, '任务已删除', 'success');
                
                if (this.statusCheckInterval) {
                    clearInterval(this.statusCheckInterval);
                    this.statusCheckInterval = null;
                }
                
                this.currentTaskId = null;
            } else {
                alert(`删除失败: ${result.error || result.message}`);
            }
        } catch (error) {
            alert(`删除失败: ${error.message}`);
        }
    }

    getStatusText(status) {
        const statusMap = {
            'pending': '等待中',
            'processing': '处理中',
            'completed': '已完成',
            'failed': '失败'
        };
        return statusMap[status] || status;
    }

    // 全局方法，供HTML中的onclick调用
    proceedWithGeneration() {
        // 触发生成按钮点击
        this.handleGeneration();
    }

    retryGeneration() {
        // 重新触发生成
        this.handleGeneration();
    }

    async previewContent(taskId) {
        // 预览功能的实现
        alert('预览功能开发中...');
    }

    async downloadFile(fileName, fileType) {
        try {
            // 使用配置管理器获取API基础URL构建完整的、绝对的下载URL
            // 确保无论应用程序如何部署，下载链接都是正确的
            const downloadUrl = `${getApiBaseUrl()}/api/gender_book/download/${fileType}/${fileName}`;
            
            // 创建临时链接并触发下载
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = fileName; // 提示浏览器以此文件名保存
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
        } catch (error) {
            console.error('下载文件失败:', error);
            alert('下载失败，请检查浏览器控制台获取更多信息。');
        }
    }

    handleAttachmentPreview() {
        const attachmentsInput = this.element.querySelector('#gender-book-attachments-input');
        const previewArea = this.element.querySelector('#attachment-preview');
        
        if (attachmentsInput.files.length === 0) {
            previewArea.innerHTML = '';
            return;
        }
        
        const fileList = Array.from(attachmentsInput.files).map(file => {
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            return `
                <div class="attachment-item">
                    <span class="attachment-name">${file.name}</span>
                    <span class="attachment-size">(${fileSize} MB)</span>
                </div>
            `;
        }).join('');
        
        previewArea.innerHTML = `
            <div class="attachment-list">
                <h5>已选择的附件 (${attachmentsInput.files.length}个):</h5>
                ${fileList}
            </div>
        `;
    }
}

// 全局变量，供HTML中的onclick调用
let genderBookGenerator = null;