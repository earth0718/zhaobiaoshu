document.addEventListener('DOMContentLoaded', () => {
    const tenderSection = document.getElementById('tender-section');
    const parserSection = document.getElementById('parser-section');
    const filterSection = document.getElementById('filter-section');
    const historySection = document.getElementById('history-section');

    // 初始化所有组件
    new TenderGenerator(tenderSection);
    new DocumentParser(parserSection);
    new FilterProcessor(filterSection);
    new HistoryViewer(historySection);

    // 设置初始视图
    ui.showSection('tender-section');

    // 检查系统状态
    api.checkHealth().then(health => {
        ui.updateSystemStatus(health.status);
    }).catch(error => {
        console.error('Health check failed:', error);
        ui.updateSystemStatus('unhealthy');
    });
});