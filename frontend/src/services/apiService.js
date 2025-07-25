/**
 * API服务层
 * 统一处理所有HTTP请求
 */

import axios from 'axios';
import {
  API_CONFIG,
  DOCUMENT_ENDPOINTS,
  TENDER_ENDPOINTS,
  DEFAULT_PARAMS,
  ERROR_MESSAGES,
} from '../config/apiConfig';

// 创建axios实例
const createApiInstance = (baseURL, timeout) => {
  const instance = axios.create({
    baseURL,
    timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 请求拦截器
  instance.interceptors.request.use(
    (config) => {
      console.log(`API请求: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('请求拦截器错误:', error);
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  instance.interceptors.response.use(
    (response) => {
      console.log(`API响应: ${response.status} ${response.config.url}`);
      return response;
    },
    (error) => {
      console.error('API错误:', error);
      return Promise.reject(handleApiError(error));
    }
  );

  return instance;
};

// 创建API实例
const documentApi = createApiInstance(
  API_CONFIG.DOCUMENT_SERVICE.BASE_URL,
  API_CONFIG.DOCUMENT_SERVICE.TIMEOUT
);

const tenderApi = createApiInstance(
  API_CONFIG.TENDER_SERVICE.BASE_URL,
  API_CONFIG.TENDER_SERVICE.TIMEOUT
);

// 错误处理函数
const handleApiError = (error) => {
  if (error.response) {
    // 服务器响应错误
    const { status, data } = error.response;
    switch (status) {
      case 400:
        return new Error(data.detail || '请求参数错误');
      case 404:
        return new Error('请求的资源不存在');
      case 500:
        return new Error(ERROR_MESSAGES.SERVER_ERROR);
      default:
        return new Error(data.detail || ERROR_MESSAGES.UNKNOWN_ERROR);
    }
  } else if (error.request) {
    // 网络错误
    return new Error(ERROR_MESSAGES.NETWORK_ERROR);
  } else if (error.code === 'ECONNABORTED') {
    // 超时错误
    return new Error(ERROR_MESSAGES.TIMEOUT);
  } else {
    return new Error(ERROR_MESSAGES.UNKNOWN_ERROR);
  }
};

// 文件上传辅助函数
const createFormData = (file, additionalData = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  
  Object.entries(additionalData).forEach(([key, value]) => {
    formData.append(key, value);
  });
  
  return formData;
};

// 文档解析服务
export const documentService = {
  // 健康检查
  async checkHealth() {
    const response = await documentApi.get(DOCUMENT_ENDPOINTS.HEALTH);
    return response.data;
  },

  // 获取系统信息
  async getSystemInfo() {
    const response = await documentApi.get(DOCUMENT_ENDPOINTS.INFO);
    return response.data;
  },

  // 解析单个文档
  async parseDocument(file, options = {}) {
    const params = { ...DEFAULT_PARAMS.DOCUMENT_PARSE, ...options };
    const formData = createFormData(file);
    
    const response = await documentApi.post(
      DOCUMENT_ENDPOINTS.PARSE,
      formData,
      {
        params,
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  // 批量解析文档
  async parseDocumentsBatch(files, options = {}) {
    const params = { ...DEFAULT_PARAMS.DOCUMENT_PARSE, ...options };
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    const response = await documentApi.post(
      DOCUMENT_ENDPOINTS.PARSE_BATCH,
      formData,
      {
        params,
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  // 提取纯文本
  async extractText(file, maxLength = null) {
    const formData = createFormData(file);
    const params = maxLength ? { max_length: maxLength } : {};
    
    const response = await documentApi.post(
      DOCUMENT_ENDPOINTS.EXTRACT_TEXT,
      formData,
      {
        params,
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  // 提取结构化数据
  async extractStructured(file, targetTypes = null) {
    const formData = createFormData(file);
    const params = targetTypes ? { target_types: targetTypes } : {};
    
    const response = await documentApi.post(
      DOCUMENT_ENDPOINTS.EXTRACT_STRUCTURED,
      formData,
      {
        params,
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  // 获取支持的文件格式
  async getSupportedFormats() {
    const response = await documentApi.get(DOCUMENT_ENDPOINTS.FORMATS);
    return response.data;
  },

  // 验证文件格式
  async validateFileFormat(filename) {
    const response = await documentApi.get(
      `${DOCUMENT_ENDPOINTS.VALIDATE}/${encodeURIComponent(filename)}`
    );
    return response.data;
  },
};

// 招标书生成服务
export const tenderService = {
  // 健康检查
  async checkHealth() {
    const response = await tenderApi.get(TENDER_ENDPOINTS.HEALTH);
    return response.data;
  },

  // 生成招标书
  async generateTender(file, options = {}) {
    const params = { ...DEFAULT_PARAMS.TENDER_GENERATE, ...options };
    const formData = createFormData(file, params);
    
    const response = await tenderApi.post(
      TENDER_ENDPOINTS.GENERATE,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  // 查询任务状态
  async getTaskStatus(taskId) {
    const response = await tenderApi.get(`${TENDER_ENDPOINTS.STATUS}/${taskId}`);
    return response.data;
  },

  // 获取可用模型
  async getAvailableModels() {
    const response = await tenderApi.get(TENDER_ENDPOINTS.MODELS);
    return response.data;
  },

  // 切换模型
  async switchModel(moduleName, provider) {
    const response = await tenderApi.post(TENDER_ENDPOINTS.SWITCH_MODEL, {
      module_name: moduleName,
      provider: provider,
    });
    return response.data;
  },

  // 获取所有任务
  async getAllTasks() {
    const response = await tenderApi.get(TENDER_ENDPOINTS.TASKS);
    return response.data;
  },

  // 删除任务
  async deleteTask(taskId) {
    const response = await tenderApi.delete(`${TENDER_ENDPOINTS.DELETE_TASK}/${taskId}`);
    return response.data;
  },
};

// 通用工具函数
export const apiUtils = {
  // 检查文件大小
  validateFileSize(file) {
    return file.size <= API_CONFIG.UPLOAD.MAX_FILE_SIZE;
  },

  // 检查文件类型
  validateFileType(file) {
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    return API_CONFIG.UPLOAD.ALLOWED_TYPES.includes(extension);
  },

  // 格式化文件大小
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  // 获取文件类型描述
  getFileTypeDescription(file) {
    return FILE_TYPE_MAP[file.type] || '未知文件类型';
  },
};