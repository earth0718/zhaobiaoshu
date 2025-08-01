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
                <!-- 生成方式选择 -->
                <div class="generation-mode form-group">
                    <label>生成方式:</label>
                    <div class="radio-group">
                        <label><input type="radio" name="generation-mode" value="file" checked> 文件上传</label>
                        <label><input type="radio" name="generation-mode" value="text"> 文本输入</label>
                    </div>
                </div>
                
                <!-- 文件上传区域 -->
                <div id="file-upload-area" class="upload-area form-group">
                    <div class="upload-mode-selector">
                        <label><input type="radio" name="upload-mode" value="single" checked> 单文件上传</label>
                        <label><input type="radio" name="upload-mode" value="multiple"> 多文件上传</label>
                    </div>
                    
                    <div id="single-file-area">
                        <label for="tender-file-input">选择文档文件 (PDF/DOCX):</label>
                        <input type="file" id="tender-file-input" accept=".pdf,.docx">
                    </div>
                    
                    <div id="multiple-file-area" style="display: none;">
                        <label for="tender-multiple-files">选择多个文档文件 (PDF/DOCX):</label>
                        <input type="file" id="tender-multiple-files" accept=".pdf,.docx" multiple>
                        <div id="file-list" class="file-list"></div>
                        
                        <div class="multiple-options">
                            <label for="tender-project-name-multi">项目名称:</label>
                            <input type="text" id="tender-project-name-multi" placeholder="请输入项目名称" value="多文件招标项目">
                            
                            <label for="tender-custom-requirements-multi">特殊要求 (可选):</label>
                            <textarea id="tender-custom-requirements-multi" rows="3" placeholder="请输入特殊要求或补充说明..."></textarea>
                        </div>
                    </div>
                </div>
                
                <!-- 文本输入区域 -->
                <div id="text-input-area" class="text-area form-group" style="display: none;">
                    <label for="tender-text-input">输入项目需求描述:</label>
                    <textarea id="tender-text-input" rows="8" placeholder="请输入项目的详细需求描述，包括项目背景、技术要求、服务内容等信息..."></textarea>
                    
                    <label for="tender-project-name">项目名称:</label>
                    <input type="text" id="tender-project-name" placeholder="请输入项目名称" value="招标项目">
                    
                    <label for="tender-custom-requirements">特殊要求 (可选):</label>
                    <textarea id="tender-custom-requirements" rows="3" placeholder="请输入特殊要求或补充说明..."></textarea>
                </div>
                
                <!-- 通用选项 -->
                <div class="options-area form-group">
                    <label for="tender-model-provider">模型提供商:</label>
                    <select id="tender-model-provider">
                        <option value="ollama">Ollama (本地)</option>
                        <option value="deepseek">DeepSeek (云端)</option>
                        <option value="siliconcloud" selected>SiliconCloud (云端)</option>
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
        
        // 生成方式切换
        const modeRadios = this.element.querySelectorAll('input[name="generation-mode"]');
        modeRadios.forEach(radio => {
            radio.addEventListener('change', () => this.handleModeChange());
        });
        
        // 上传模式切换
        const uploadModeRadios = this.element.querySelectorAll('input[name="upload-mode"]');
        uploadModeRadios.forEach(radio => {
            radio.addEventListener('change', () => this.handleUploadModeChange());
        });
        
        // 多文件选择变化
        const multipleFilesInput = this.element.querySelector('#tender-multiple-files');
        multipleFilesInput.addEventListener('change', () => this.handleMultipleFilesChange());
    }
    
    handleModeChange() {
        const selectedMode = this.element.querySelector('input[name="generation-mode"]:checked').value;
        const fileUploadArea = this.element.querySelector('#file-upload-area');
        const textInputArea = this.element.querySelector('#text-input-area');
        
        if (selectedMode === 'file') {
            fileUploadArea.style.display = 'block';
            textInputArea.style.display = 'none';
        } else {
            fileUploadArea.style.display = 'none';
            textInputArea.style.display = 'block';
        }
    }
    
    handleUploadModeChange() {
        const selectedUploadMode = this.element.querySelector('input[name="upload-mode"]:checked').value;
        const singleFileArea = this.element.querySelector('#single-file-area');
        const multipleFileArea = this.element.querySelector('#multiple-file-area');
        
        if (selectedUploadMode === 'single') {
            singleFileArea.style.display = 'block';
            multipleFileArea.style.display = 'none';
        } else {
            singleFileArea.style.display = 'none';
            multipleFileArea.style.display = 'block';
        }
    }
    
    handleMultipleFilesChange() {
        const multipleFilesInput = this.element.querySelector('#tender-multiple-files');
        const fileListDiv = this.element.querySelector('#file-list');
        
        fileListDiv.innerHTML = '';
        
        if (multipleFilesInput.files.length > 0) {
            const fileList = document.createElement('ul');
            fileList.className = 'selected-files';
            
            Array.from(multipleFilesInput.files).forEach((file, index) => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                `;
                fileList.appendChild(listItem);
            });
            
            fileListDiv.appendChild(fileList);
            
            const summary = document.createElement('p');
            summary.className = 'file-summary';
            summary.textContent = `已选择 ${multipleFilesInput.files.length} 个文件`;
            fileListDiv.appendChild(summary);
        }
    }

    async handleGenerate() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }

        const selectedMode = this.element.querySelector('input[name="generation-mode"]:checked').value;
        const modelProvider = this.element.querySelector('#tender-model-provider').value;
        const qualityLevel = this.element.querySelector('#tender-quality-level').value;
        const resultArea = this.element.querySelector('#tender-result');

        ui.showMessage(resultArea, '正在创建生成任务...', 'info');

        try {
            let task;
            
            if (selectedMode === 'file') {
                // 文件上传模式
                const selectedUploadMode = this.element.querySelector('input[name="upload-mode"]:checked').value;
                
                if (selectedUploadMode === 'single') {
                    // 单文件上传
                    const fileInput = this.element.querySelector('#tender-file-input');
                    
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

                    task = await api.generateTender(formData, params);
                } else {
                    // 多文件上传
                    const multipleFilesInput = this.element.querySelector('#tender-multiple-files');
                    const projectNameInput = this.element.querySelector('#tender-project-name-multi');
                    const customRequirementsInput = this.element.querySelector('#tender-custom-requirements-multi');
                    
                    if (multipleFilesInput.files.length === 0) {
                        ui.showMessage(resultArea, '请先选择至少一个文件。', 'error');
                        return;
                    }

                    const formData = new FormData();
                    Array.from(multipleFilesInput.files).forEach(file => {
                        formData.append('files', file);
                    });
                    
                    formData.append('model_provider', modelProvider);
                    formData.append('quality_level', qualityLevel);
                    formData.append('project_name', projectNameInput.value.trim() || '多文件招标项目');
                    
                    const customRequirements = customRequirementsInput.value.trim();
                    if (customRequirements) {
                        formData.append('custom_requirements', customRequirements);
                    }

                    task = await api.generateMultipleTender(formData);
                }
            } else {
                // 文本输入模式
                const textInput = this.element.querySelector('#tender-text-input');
                const projectNameInput = this.element.querySelector('#tender-project-name');
                const customRequirementsInput = this.element.querySelector('#tender-custom-requirements');
                
                const textContent = textInput.value.trim();
                const projectName = projectNameInput.value.trim() || '招标项目';
                const customRequirements = customRequirementsInput.value.trim();
                
                if (!textContent || textContent.length < 10) {
                    ui.showMessage(resultArea, '请输入至少10个字符的项目需求描述。', 'error');
                    return;
                }

                task = await api.generateTenderFromText(
                    textContent,
                    modelProvider,
                    qualityLevel,
                    projectName,
                    customRequirements
                );
            }
            
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