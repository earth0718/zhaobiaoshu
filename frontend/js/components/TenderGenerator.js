class TenderGenerator {
    constructor(element) {
        this.element = element;
        this.pollingInterval = null;
        this.render();
        this.attachEventListeners();
    }

    render() {
        this.element.innerHTML = `
            <div class="tender-container">
                <div class="upload-area form-group">
                    <label for="tender-file-input">选择文档文件 (PDF/DOCX):</label>
                    <input type="file" id="tender-file-input" accept=".pdf,.docx">
                </div>
                <div class="options-area form-group">
                    <label for="tender-model-provider">模型提供商:</label>
                    <select id="tender-model-provider">
                        <option value="ollama">Ollama (本地)</option>
                        <option value="deepseek">DeepSeek (云端)</option>
                    </select>
                    <label for="tender-quality-level">生成质量:</label>
                    <select id="tender-quality-level">
                        <option value="standard">标准</option>
                        <option value="basic">基础</option>
                        <option value="premium">高级</option>
                    </select>
                </div>
                <div class="form-group">
                    <button id="tender-submit-btn" class="btn-primary">生成招标书</button>
                </div>
                <div id="tender-result" class="result-area"></div>
            </div>
        `;
    }

    attachEventListeners() {
        const submitBtn = this.element.querySelector('#tender-submit-btn');
        submitBtn.addEventListener('click', () => this.handleGenerate());
    }

    async handleGenerate() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }

        const fileInput = this.element.querySelector('#tender-file-input');
        const modelProvider = this.element.querySelector('#tender-model-provider').value;
        const qualityLevel = this.element.querySelector('#tender-quality-level').value;
        const resultArea = this.element.querySelector('#tender-result');

        if (fileInput.files.length === 0) {
            ui.showMessage(resultArea, '请先选择一个文件。', 'error');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        const params = new URLSearchParams({
            model_provider: modelProvider,
            quality_level: qualityLevel
        });

        ui.showMessage(resultArea, '正在创建生成任务...', 'info');

        try {
            const task = await api.generateTender(formData, params);
            if (task.task_id) {
                ui.showMessage(resultArea, `任务已创建: ${task.task_id}。正在处理中...`, 'info');
                this.pollStatus(task.task_id);
            } else {
                ui.showMessage(resultArea, `任务创建失败: ${task.detail || '未知错误'}`, 'error');
            }
        } catch (error) {
            ui.showMessage(resultArea, `请求失败: ${error.message}`, 'error');
        }
    }

    pollStatus(taskId) {
        const resultArea = this.element.querySelector('#tender-result');
        this.pollingInterval = setInterval(async () => {
            try {
                const status = await api.getTaskStatus(taskId);
                if (status.status === 'completed') {
                    clearInterval(this.pollingInterval);
                    ui.showMessage(resultArea, '招标文件生成完成！', 'success');
                    ui.renderJSON(resultArea, status.result);
                } else if (status.status === 'failed') {
                    clearInterval(this.pollingInterval);
                    ui.showMessage(resultArea, `处理失败: ${status.message}`, 'error');
                } else {
                    ui.showMessage(resultArea, `处理中: ${status.message} (${status.progress || 0}%)`, 'info');
                }
            } catch (error) {
                clearInterval(this.pollingInterval);
                ui.showMessage(resultArea, `查询状态失败: ${error.message}`, 'error');
            }
        }, 3000);
    }
}