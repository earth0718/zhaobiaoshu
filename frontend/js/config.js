/**
 * 前端配置管理模块
 * 负责加载和管理用户可配置的变量
 */

class ConfigManager {
    constructor() {
        this.config = null;
        this.defaultConfig = {
            api: {
            base_url: 'http://localhost:8001',
                timeout_ms: 60000,
                retry_attempts: 3
            },
            ui: {
                status_polling_interval_ms: 3000,
                auto_cleanup_blob_urls_ms: 60000,
                max_file_size_mb: 50
            },
            download: {
                default_filename_prefix: '投标书',
                supported_formats: ['word', 'markdown'],
                fallback_format: 'txt'
            },
            generation: {
                default_model_provider: 'deepseek',
                enable_optimization_default: true,
                include_analysis_default: true
            }
        };
    }

    /**
     * 异步加载配置文件
     * @returns {Promise<Object>} 配置对象
     */
    async loadConfig() {
        try {
            const response = await fetch('/config/frontend_config.json');
            if (response.ok) {
                this.config = await response.json();
                console.log('配置文件加载成功:', this.config);
            } else {
                console.warn('配置文件加载失败，使用默认配置');
                this.config = this.defaultConfig;
            }
        } catch (error) {
            console.warn('配置文件加载异常，使用默认配置:', error);
            this.config = this.defaultConfig;
        }
        
        // 将配置暴露为全局变量
        window.APP_CONFIG = this.config;
        window.API_BASE_URL = this.config.api.base_url;
        
        return this.config;
    }

    /**
     * 获取配置值
     * @param {string} path 配置路径，如 'api.base_url'
     * @param {*} defaultValue 默认值
     * @returns {*} 配置值
     */
    get(path, defaultValue = null) {
        if (!this.config) {
            console.warn('配置尚未加载，返回默认值');
            return defaultValue;
        }
        
        const keys = path.split('.');
        let value = this.config;
        
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return defaultValue;
            }
        }
        
        return value;
    }

    /**
     * 获取API基础URL
     * @returns {string} API基础URL
     */
    getApiBaseUrl() {
        return this.get('api.base_url', 'http://localhost:8000');
    }

    /**
     * 获取状态轮询间隔
     * @returns {number} 轮询间隔（毫秒）
     */
    getStatusPollingInterval() {
        return this.get('ui.status_polling_interval_ms', 3000);
    }

    /**
     * 获取请求超时时间
     * @returns {number} 超时时间（毫秒）
     */
    getRequestTimeout() {
        return this.get('api.timeout_ms', 60000);
    }

    /**
     * 获取默认模型提供商
     * @returns {string} 模型提供商
     */
    getDefaultModelProvider() {
        return this.get('generation.default_model_provider', 'deepseek');
    }

    /**
     * 获取默认优化设置
     * @returns {boolean} 是否启用优化
     */
    getDefaultOptimizationSetting() {
        return this.get('generation.enable_optimization_default', true);
    }

    /**
     * 获取默认分析设置
     * @returns {boolean} 是否包含分析
     */
    getDefaultAnalysisSetting() {
        return this.get('generation.include_analysis_default', true);
    }
}

// 创建全局配置管理器实例
const configManager = new ConfigManager();

// 暴露为全局变量
window.configManager = configManager;

// 导出配置管理器（如果支持模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = configManager;
}