const ui = {
    showSection: (sectionId) => {
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionId).classList.add('active');

        document.querySelectorAll('nav button').forEach(button => {
            button.classList.remove('active');
        });
        document.getElementById(`nav-${sectionId.split('-')[0]}`).classList.add('active');
    },

    updateSystemStatus: (status) => {
        const statusElement = document.getElementById('system-status');
        if (status === 'healthy') {
            statusElement.textContent = '运行正常';
            statusElement.style.color = 'green';
        } else {
            statusElement.textContent = '连接失败';
            statusElement.style.color = 'red';
        }
    },

    renderJSON: (element, data) => {
        const pre = document.createElement('pre');
        pre.style.backgroundColor = '#f0f0f0';
        pre.style.padding = '15px';
        pre.style.borderRadius = '5px';
        pre.style.whiteSpace = 'pre-wrap';
        pre.style.wordWrap = 'break-word';
        pre.textContent = JSON.stringify(data, null, 2);
        element.innerHTML = '';
        element.appendChild(pre);
    },

    showMessage: (element, message, type = 'info') => {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;
        element.innerHTML = '';
        element.appendChild(messageElement);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nav-tender').addEventListener('click', () => ui.showSection('tender-section'));
    document.getElementById('nav-parser').addEventListener('click', () => ui.showSection('parser-section'));
    document.getElementById('nav-filter').addEventListener('click', () => ui.showSection('filter-section'));
    document.getElementById('nav-history').addEventListener('click', () => ui.showSection('history-section'));
});