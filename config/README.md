# 配置文件说明

本目录包含系统的各种配置文件，用于管理用户可修改的变量和设置。

## 前端配置

### frontend_config.json

前端应用的主要配置文件，包含以下配置项：

#### API配置
- `api.base_url`: API服务器地址（默认: http://localhost:8000）
- `api.timeout_ms`: API请求超时时间，单位毫秒（默认: 60000）
- `api.retry_attempts`: API请求失败重试次数（默认: 3）

#### UI配置
- `ui.status_polling_interval_ms`: 任务状态轮询间隔，单位毫秒（默认: 3000）
- `ui.auto_cleanup_blob_urls_ms`: 自动清理下载链接的时间，单位毫秒（默认: 60000）
- `ui.max_file_size_mb`: 最大文件上传大小，单位MB（默认: 50）

#### 下载配置
- `download.default_filename_prefix`: 下载文件的默认前缀名称（默认: "投标书"）
- `download.supported_formats`: 支持的下载格式列表（默认: ["word", "markdown"]）
- `download.fallback_format`: 后备下载格式（默认: "txt"）

#### 生成配置
- `generation.default_model_provider`: 默认AI模型提供商（默认: "deepseek"）
- `generation.enable_optimization_default`: 默认是否启用智能优化（默认: true）
- `generation.include_analysis_default`: 默认是否包含章节分析（默认: true）

### 使用方法

1. 复制 `frontend_config_example.json` 为 `frontend_config.json`
2. 根据需要修改配置值
3. 重新加载页面使配置生效

### 示例

```json
{
  "api": {
    "base_url": "http://your-server.com:8080",
    "timeout_ms": 120000
  },
  "ui": {
    "status_polling_interval_ms": 5000
  },
  "generation": {
    "default_model_provider": "ollama",
    "enable_optimization_default": false
  }
}
```

## 其他配置文件

### model_config.json
模型相关配置

### parser_config.py
文档解析器配置

### settings.py
系统设置配置

### tender_generation_config.ini
招标文件生成配置

### ollama_speed_config.ini
Ollama模型速度优化配置

## 注意事项

1. 修改配置文件后需要重新加载页面
2. 配置文件使用JSON格式，请确保语法正确
3. 如果配置文件不存在或格式错误，系统将使用默认配置
4. 建议在修改前备份原配置文件
5. 配置文件中的注释字段（以`_comment`开头）仅用于说明，不会影响功能