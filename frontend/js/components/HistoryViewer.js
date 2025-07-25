class HistoryViewer {
    constructor(element) {
        this.element = element;
        this.page = 1;
        this.limit = 10;
        this.render();
        this.attachEventListeners();
        this.loadHistory();
    }

    render() {
        this.element.innerHTML = `
            <div class="history-container">
                <div class="history-controls form-group">
                    <button id="refresh-history-btn" class="btn-secondary">刷新</button>
                    <button id="prev-page-btn" class="btn-secondary">上一页</button>
                    <span id="page-info">第 ${this.page} 页</span>
                    <button id="next-page-btn" class="btn-secondary">下一页</button>
                </div>
                <div id="history-list" class="history-list"></div>
            </div>
        `;
    }

    attachEventListeners() {
        this.element.querySelector('#refresh-history-btn').addEventListener('click', () => this.loadHistory());
        this.element.querySelector('#prev-page-btn').addEventListener('click', () => this.changePage(-1));
        this.element.querySelector('#next-page-btn').addEventListener('click', () => this.changePage(1));
        this.element.addEventListener('click', (event) => {
            if (event.target.classList.contains('delete-record-btn')) {
                const recordId = event.target.dataset.id;
                if (confirm('确定要删除这条记录吗？')) {
                    this.deleteRecord(recordId);
                }
            }
            if (event.target.classList.contains('export-record-btn')) {
                const recordId = event.target.dataset.id;
                this.exportRecord(recordId);
            }
            if (event.target.classList.contains('view-details-btn')) {
                const details = JSON.parse(event.target.dataset.details);
                ui.renderJson(this.element.querySelector(`#details-${event.target.dataset.id}`), details);
                event.target.style.display = 'none';
            }
        });
    }

    changePage(direction) {
        if (this.page + direction > 0) {
            this.page += direction;
            this.element.querySelector('#page-info').textContent = `第 ${this.page} 页`;
            this.loadHistory();
        }
    }

    async loadHistory() {
        const historyList = this.element.querySelector('#history-list');
        ui.showMessage(historyList, '正在加载历史记录...', 'info');

        try {
            const params = new URLSearchParams({
                skip: (this.page - 1) * this.limit,
                limit: this.limit
            });
            const history = await api.getHistory(params);
            this.renderHistory(history.records);
            this.element.querySelector('#prev-page-btn').disabled = this.page === 1;
            this.element.querySelector('#next-page-btn').disabled = history.records.length < this.limit;
        } catch (error) {
            ui.showMessage(historyList, `加载历史记录失败: ${error.message}`, 'error');
        }
    }

    renderHistory(records) {
        const historyList = this.element.querySelector('#history-list');
        if (!records || records.length === 0) {
            historyList.innerHTML = '没有更多历史记录了。';
            if(this.page === 1) this.element.querySelector('#prev-page-btn').disabled = true;
            this.element.querySelector('#next-page-btn').disabled = true;
            return;
        }

        const listHtml = records.map(record => `
            <div class="history-record">
                <p><strong>ID:</strong> ${record.id}</p>
                <p><strong>时间:</strong> ${new Date(record.timestamp).toLocaleString()}</p>
                <p><strong>操作:</strong> ${record.action_type}</p>
                <p><strong>文件名:</strong> ${record.filename || 'N/A'}</p>
                <p><strong>状态:</strong> <span class="status-${record.status.toLowerCase()}">${record.status}</span></p>
                <div class="record-actions">
                    <button class="btn-secondary view-details-btn" data-id="${record.id}" data-details='${JSON.stringify(record.details)}'>查看详情</button>
                    <button class="btn-danger delete-record-btn" data-id="${record.id}">删除</button>
                    <button class="btn-secondary export-record-btn" data-id="${record.id}">导出</button>
                </div>
                <div id="details-${record.id}" class="details-view"></div>
            </div>
        `).join('');

        historyList.innerHTML = listHtml;
    }

    async deleteRecord(recordId) {
        try {
            await api.deleteHistoryRecord(recordId);
            ui.showMessage(this.element.querySelector('#history-list'), '记录已删除。', 'success');
            this.loadHistory(); // Refresh the list
        } catch (error) {
            ui.showMessage(this.element.querySelector('#history-list'), `删除失败: ${error.message}`, 'error');
        }
    }

    async exportRecord(recordId) {
        try {
            const blob = await api.exportHistoryRecord(recordId);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `history_${recordId}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } catch (error) {
            ui.showMessage(this.element.querySelector('#history-list'), `导出失败: ${error.message}`, 'error');
        }
    }
}