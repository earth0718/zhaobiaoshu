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
                ui.renderJSON(resultArea, result.data);
            } else {
                ui.showMessage(resultArea, `解析失败: ${result.error || result.message}`, 'error');
            }
        } catch (error) {
            ui.showMessage(resultArea, `请求失败: ${error.message}`, 'error');
        }
    }
}