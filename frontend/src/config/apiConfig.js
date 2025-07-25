/**
 * API配置文件
 * 包含所有API端点和可配置参数
 */

// 基础配置
export const API_CONFIG = {
  // 文档解析服务
  DOCUMENT_SERVICE: {
    BASE_URL: process.env.REACT_APP_DOCUMENT_API_URL || 'http://localhost:8000',
    PREFIX: '/api/v1/document',
    TIMEOUT: 30000, // 30秒超时
  },
  
  // 招标书生成服务
  TENDER_SERVICE: {
    BASE_URL: process.env.REACT_APP_TENDER_API_URL || 'http://localhost:8001',
    PREFIX: '/api/v1/tender',
    TIMEOUT: 60000, // 60秒超时
  },
  
  // 轮询配置
  POLLING: {
    INTERVAL: 2000, // 2秒轮询间隔
    MAX_ATTEMPTS: 150, // 最大轮询次数（5分钟）
  },
  
  // 文件上传配置
  UPLOAD: {
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    ALLOWED_TYPES: ['.pdf', '.docx', '.doc', '.txt', '.md'],
    CHUNK_SIZE: 1024 * 1024, // 1MB分块上传
  },
};

// 文档解析API端点
export const DOCUMENT_ENDPOINTS = {
  // 系统信息
  HEALTH: '/health',
  INFO: '/info',
  
  // 文档解析
  PARSE: `${API_CONFIG.DOCUMENT_SERVICE.PREFIX}/parse`,
  PARSE_BATCH: `${API_CONFIG.DOCUMENT_SERVICE.PREFIX}/parse/batch`,
  EXTRACT_TEXT: `${API_CONFIG.DOCUMENT_SERVICE.PREFIX}/extract/text`,
  EXTRACT_STRUCTURED: `${API_CONFIG.DOCUMENT_SERVICE.PREFIX}/extract/structured`,
  
  // 工具接口
  FORMATS: `${API_CONFIG.DOCUMENT_SERVICE.PREFIX}/formats`,
  VALIDATE: `${API_CONFIG.DOCUMENT_SERVICE.PREFIX}/validate`,
  SERVICE_HEALTH: `${API_CONFIG.DOCUMENT_SERVICE.PREFIX}/health`,
};

// 招标书生成API端点
export const TENDER_ENDPOINTS = {
  // 招标书生成
  GENERATE: `${API_CONFIG.TENDER_SERVICE.PREFIX}/generate`,
  STATUS: `${API_CONFIG.TENDER_SERVICE.PREFIX}/status`,
  
  // 模型管理
  MODELS: `${API_CONFIG.TENDER_SERVICE.PREFIX}/models`,
  SWITCH_MODEL: `${API_CONFIG.TENDER_SERVICE.PREFIX}/models/switch`,
  
  // 任务管理
  TASKS: `${API_CONFIG.TENDER_SERVICE.PREFIX}/tasks`,
  DELETE_TASK: `${API_CONFIG.TENDER_SERVICE.PREFIX}/tasks`,
  
  // 健康检查
  HEALTH: `${API_CONFIG.TENDER_SERVICE.PREFIX}/health`,
};

// 默认请求参数
export const DEFAULT_PARAMS = {
  // 文档解析默认参数
  DOCUMENT_PARSE: {
    include_metadata: true,
    cleanup: true,
    max_pages_per_batch: 5,
  },
  
  // 招标书生成默认参数
  TENDER_GENERATE: {
    model_provider: 'ollama',
    quality_level: 'standard',
  },
};

// 状态映射
export const STATUS_MAP = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

// 质量级别选项
export const QUALITY_LEVELS = [
  { value: 'basic', label: '基础质量', description: '快速生成，基本格式' },
  { value: 'standard', label: '标准质量', description: '平衡速度和质量' },
  { value: 'premium', label: '高级质量', description: '最佳质量，处理时间较长' },
];

// 模型提供商选项
export const MODEL_PROVIDERS = [
  { value: 'ollama', label: 'Ollama本地模型', description: '本地部署，数据安全' },
  { value: 'deepseek', label: 'DeepSeek云端模型', description: '云端服务，性能强劲' },
];

// 文件类型映射
export const FILE_TYPE_MAP = {
  'application/pdf': 'PDF文档',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word文档(.docx)',
  'application/msword': 'Word文档(.doc)',
  'text/plain': '纯文本文件',
  'text/markdown': 'Markdown文件',
};

// 错误消息映射
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  FILE_TOO_LARGE: `文件大小超过限制（${API_CONFIG.UPLOAD.MAX_FILE_SIZE / 1024 / 1024}MB）`,
  UNSUPPORTED_FORMAT: '不支持的文件格式',
  UPLOAD_FAILED: '文件上传失败',
  PARSE_FAILED: '文档解析失败',
  GENERATION_FAILED: '招标书生成失败',
  TIMEOUT: '请求超时，请稍后重试',
  SERVER_ERROR: '服务器内部错误',
  UNKNOWN_ERROR: '未知错误，请联系管理员',
};