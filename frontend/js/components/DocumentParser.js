class DocumentParser {
    constructor(element) {
        this.element = element;
        this.render();
        this.attachEventListeners();
    }

    render() {
        this.element.innerHTML = `
            <div class="parser-container">
                <div class="upload-area form-group">
                    <label for="parser-file-input">选择文档文件:</label>
                    <input type="file" id="parser-file-input" accept=".pdf,.doc,.docx,.txt,.md">
                </div>
                <div class="options-area form-group">
                    <label><input type="checkbox" id="parser-include-metadata" checked> 包含元数据</label>
                    <label><input type="checkbox" id="parser-cleanup" checked> 清理临时文件</label>
                    <label for="parser-max-pages">PDF每批最大页数:</label>
                    <input type="number" id="parser-max-pages" value="5" min="1" max="20">
                </div>
                <div class="form-group">
                    <button id="parser-submit-btn" class="btn-primary">解析文档</button>
                </div>
                <div id="parser-result" class="result-area"></div>
            </div>
        `;
    }

    attachEventListeners() {
        const submitBtn = this.element.querySelector('#parser-submit-btn');
        submitBtn.addEventListener('click', () => this.handleParse());
    }

    async handleParse() {
        const fileInput = this.element.querySelector('#parser-file-input');
        const resultArea = this.element.querySelector('#parser-result');
        const includeMetadata = this.element.querySelector('#parser-include-metadata').checked;
        const cleanup = this.element.querySelector('#parser-cleanup').checked;
        const maxPages = this.element.querySelector('#parser-max-pages').value;

        if (fileInput.files.length === 0) {
            ui.showMessage(resultArea, '请先选择一个文件。', 'error');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        const params = new URLSearchParams({
            include_metadata: includeMetadata,
            cleanup: cleanup,
            max_pages_per_batch: maxPages
        });

        ui.showMessage(resultArea, '正在解析文档，请稍候...', 'info');

        try {
            const result = await api.parseDocument(formData, params);
            if (result.success) {
                this.createDownloadLink(resultArea, result.data, file.name);
            } else {
                ui.showMessage(resultArea, `解析失败: ${result.error || result.message}`, 'error');
            }
        } catch (error) {
            ui.showMessage(resultArea, `请求失败: ${error.message}`, 'error');
        }
    }

    createDownloadLink(resultArea, data, originalFileName) {
        // 创建JSON文件内容
        const jsonContent = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        // 生成下载文件名
        const baseName = originalFileName.replace(/\.[^/.]+$/, ""); // 移除原文件扩展名
        const downloadFileName = `${baseName}_解析结果.json`;
        
        // 创建下载链接HTML
        const downloadHtml = `
            <div class="download-container">
                <div class="success-message">
                    <i class="icon-success">✓</i>
                    <span>文档解析完成！</span>
                </div>
                <div class="download-info">
                    <p><strong>原文件：</strong>${originalFileName}</p>
                    <p><strong>解析时间：</strong>${new Date().toLocaleString()}</p>
                    <p><strong>文件大小：</strong>${(blob.size / 1024).toFixed(2)} KB</p>
                </div>
                <div class="download-actions">
                    <a href="${url}" download="${downloadFileName}" class="btn-download">
                        <i class="icon-download">⬇</i>
                        下载解析结果 (JSON)
                    </a>
                    <button class="btn-preview" onclick="this.parentElement.parentElement.querySelector('.preview-area').style.display = this.parentElement.parentElement.querySelector('.preview-area').style.display === 'none' ? 'block' : 'none'">
                        <i class="icon-preview">👁</i>
                        预览内容
                    </button>
                </div>
                <div class="preview-area" style="display: none;">
                    <h4>内容预览：</h4>
                    <pre class="json-preview">${jsonContent.substring(0, 1000)}${jsonContent.length > 1000 ? '\n\n... (内容过长，请下载完整文件查看)' : ''}</pre>
                </div>
            </div>
        `;
        
        resultArea.innerHTML = downloadHtml;
        
        // 自动清理URL对象（可选，避免内存泄漏）
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 60000); // 1分钟后清理
    }
}