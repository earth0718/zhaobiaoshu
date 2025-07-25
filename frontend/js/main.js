document.addEventListener('DOMContentLoaded', () => {
    const parserSection = document.getElementById('parser-section');
    const tenderSection = document.getElementById('tender-section');
    const historySection = document.getElementById('history-section');

    // 初始化所有组件
    new DocumentParser(parserSection);
    new TenderGenerator(tenderSection);
    new HistoryViewer(historySection);

    // 设置初始视图
    ui.showSection('parser-section');

    // 检查系统状态
    api.checkHealth().then(health => {
        ui.updateSystemStatus(health.status);
    }).catch(error => {
        console.error('Health check failed:', error);
        ui.updateSystemStatus('unhealthy');
    });
});