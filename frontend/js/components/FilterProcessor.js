class FilterProcessor {
    constructor(element) {
        this.element = element;
        this.render();
        this.attachEventListeners();
    }

    render() {
        this.element.innerHTML = `
            <div class="filter-container">
                <div class="upload-area form-group">
                    <label for="filter-file-input">选择JSON文件:</label>
                    <input type="file" id="filter-file-input" accept=".json">
                    <small class="help-text">请上传文档解析后生成的JSON文件</small>
                </div>
                <div class="filter-info form-group">
                    <h3>智能处理功能说明</h3>
                    <ul>
                        <li>智能合并相关文本片段（如电话号码、地址等）</li>
                        <li>优化文档结构，按章节组织内容</li>
                        <li>生成结构化文本和LLM友好的提示词</li>
                        <li>提供完整的处理统计和验证信息</li>
                        <li>支持多种输出格式：优化数据、结构化文本、LLM提示词</li>
                    </ul>
                </div>
                <div class="form-group">
                    <button id="filter-submit-btn" class="btn-primary">智能处理JSON文件</button>
                </div>
                <div id="filter-result" class="result-area"></div>
            </div>
        `;
    }

    attachEventListeners() {
        const submitBtn = this.element.querySelector('#filter-submit-btn');
        submitBtn.addEventListener('click', () => this.handleFilter());
    }

    async handleFilter() {
        const fileInput = this.element.querySelector('#filter-file-input');
        const resultArea = this.element.querySelector('#filter-result');

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

        ui.showMessage(resultArea, '正在智能处理JSON文件，请稍候...', 'info');

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

            // 调用后端过滤API
            const result = await api.filterJSON(jsonData);
            
            if (result.success) {
                this.createProcessedDownloadLinks(resultArea, result.data, file.name);
            } else {
                ui.showMessage(resultArea, `处理失败: ${result.error || result.message}`, 'error');
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

    createProcessedDownloadLinks(resultArea, processedData, originalFileName) {
        const { optimized_data, structured_text, llm_prompt, statistics } = processedData;
        
        // 创建多个下载文件
        const baseName = originalFileName.replace(/\.json$/i, "");
        
        // 1. 优化后的JSON数据
        const optimizedJsonContent = JSON.stringify(optimized_data, null, 2);
        const optimizedBlob = new Blob([optimizedJsonContent], { type: 'application/json' });
        const optimizedUrl = URL.createObjectURL(optimizedBlob);
        
        // 2. 结构化文本
        const structuredBlob = new Blob([structured_text], { type: 'text/plain; charset=utf-8' });
        const structuredUrl = URL.createObjectURL(structuredBlob);
        
        // 3. LLM提示词
        const promptBlob = new Blob([llm_prompt], { type: 'text/plain; charset=utf-8' });
        const promptUrl = URL.createObjectURL(promptBlob);
        
        // 创建下载链接HTML
        const downloadHtml = `
            <div class="download-container">
                <div class="success-message">
                    <i class="icon-success">✓</i>
                    <span>JSON文件智能处理完成！</span>
                </div>
                <div class="filter-stats">
                    <h4>处理统计</h4>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">原始文件:</span>
                            <span class="stat-value">${originalFileName}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">处理时间:</span>
                            <span class="stat-value">${new Date().toLocaleString()}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">原始内容块:</span>
                            <span class="stat-value">${statistics.original_content_count}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">优化后内容块:</span>
                            <span class="stat-value">${statistics.optimized_content_count}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">结构化文本长度:</span>
                            <span class="stat-value">${statistics.structured_text_length} 字符</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">LLM提示词长度:</span>
                            <span class="stat-value">${statistics.llm_prompt_length} 字符</span>
                        </div>
                    </div>
                </div>
                <div class="download-actions">
                    <a href="${optimizedUrl}" download="${baseName}_optimized.json" class="btn-download">
                        <i class="icon-download">⬇</i>
                        下载优化后的JSON
                    </a>
                    <a href="${structuredUrl}" download="${baseName}_structured.txt" class="btn-download">
                        <i class="icon-download">⬇</i>
                        下载结构化文本
                    </a>
                    <a href="${promptUrl}" download="${baseName}_llm_prompt.txt" class="btn-download">
                        <i class="icon-download">⬇</i>
                        下载LLM提示词
                    </a>
                    <button class="btn-preview" onclick="this.parentElement.parentElement.querySelector('.preview-area').style.display = this.parentElement.parentElement.querySelector('.preview-area').style.display === 'none' ? 'block' : 'none'">
                        <i class="icon-preview">👁</i>
                        预览内容
                    </button>
                </div>
                <div class="preview-area" style="display: none;">
                    <div class="preview-tabs">
                        <button class="tab-btn active" onclick="this.parentElement.parentElement.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none'); this.parentElement.parentElement.querySelector('.optimized-preview').style.display = 'block'; this.parentElement.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active')); this.classList.add('active');">优化数据</button>
                        <button class="tab-btn" onclick="this.parentElement.parentElement.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none'); this.parentElement.parentElement.querySelector('.structured-preview').style.display = 'block'; this.parentElement.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active')); this.classList.add('active');">结构化文本</button>
                        <button class="tab-btn" onclick="this.parentElement.parentElement.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none'); this.parentElement.parentElement.querySelector('.prompt-preview').style.display = 'block'; this.parentElement.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active')); this.classList.add('active');">LLM提示词</button>
                    </div>
                    <div class="tab-content optimized-preview">
                        <h4>优化后的JSON数据预览：</h4>
                        <pre class="json-preview">${optimizedJsonContent.substring(0, 800)}${optimizedJsonContent.length > 800 ? '\n\n... (内容过长，请下载完整文件查看)' : ''}</pre>
                    </div>
                    <div class="tab-content structured-preview" style="display: none;">
                        <h4>结构化文本预览：</h4>
                        <pre class="text-preview">${structured_text.substring(0, 800)}${structured_text.length > 800 ? '\n\n... (内容过长，请下载完整文件查看)' : ''}</pre>
                    </div>
                    <div class="tab-content prompt-preview" style="display: none;">
                        <h4>LLM提示词预览：</h4>
                        <pre class="text-preview">${llm_prompt.substring(0, 800)}${llm_prompt.length > 800 ? '\n\n... (内容过长，请下载完整文件查看)' : ''}</pre>
                    </div>
                </div>
            </div>
        `;
        
        resultArea.innerHTML = downloadHtml;
        
        // 自动清理URL对象
        setTimeout(() => {
            URL.revokeObjectURL(optimizedUrl);
            URL.revokeObjectURL(structuredUrl);
            URL.revokeObjectURL(promptUrl);
        }, 60000); // 1分钟后清理
    }

    countContentBlocks(data) {
        try {
            if (typeof data === 'string') {
                data = JSON.parse(data);
            }
            return data.content ? data.content.length : 0;
        } catch {
            return 0;
        }
    }
}