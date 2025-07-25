# 招标文件生成API接口文档

## 概述

招标文件生成系统现已集成到现有的文档解析系统中，提供完整的从文档解析到招标文件生成的端到端服务。

## 服务状态

- **后端服务地址**: http://localhost:8082
- **API文档**: http://localhost:8082/docs
- **前端界面**: http://localhost:3000

## 核心功能模块

### 1. LLM服务模块 (`src/llm_service/`)

**功能**: 提供统一的大语言模型调用接口

**支持的模型**:
- Ollama本地模型 (默认: qwen2.5:7b)
- DeepSeek云端模型

**主要组件**:
- `llm_connector.py`: 模型连接器，处理具体的模型调用
- `model_manager.py`: 模型管理器，统一管理多种模型
- `llm_utils.py`: 工具函数，处理响应解析和数据清理

### 2. 招标生成核心模块 (`src/tender_generation_core/`)

**功能**: 实现招标文件生成的完整流程

**主要组件**:
- `processor.py`: 核心处理器，实现Map-Reduce文档处理流程
- `parser.py`: 文档解析器，支持PDF和DOCX格式
- `chunker.py`: 智能文本分块器，使用LangChain技术
- `api.py`: REST API接口

## API接口详情

### 1. 招标文件生成接口

**POST** `/api/tender/generate`

**功能**: 上传文档并生成招标书

**请求参数**:
```bash
curl -X POST "http://localhost:8082/api/tender/generate" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf" \
  -F "model_provider=ollama" \
  -F "quality_level=standard"
```

**参数说明**:
- `file`: 要处理的文档文件（支持PDF、DOCX）
- `model_provider`: 模型提供商（ollama/deepseek，默认ollama）
- `quality_level`: 生成质量级别（basic/standard/premium，默认standard）

**响应示例**:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "任务已创建，正在处理中...",
  "status_url": "/api/tender/status/123e4567-e89b-12d3-a456-426614174000"
}
```

### 2. 任务状态查询接口

**GET** `/api/tender/status/{task_id}`

**功能**: 查询招标文件生成任务的状态

**请求示例**:
```bash
curl "http://localhost:8082/api/tender/status/123e4567-e89b-12d3-a456-426614174000"
```

**响应示例**:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "progress": 100,
  "message": "招标文件生成完成",
  "result": {
    "tender_document": "# 招标书\n\n## 第一章 采购公告\n...",
    "file_size": 15420,
    "generation_time": "2024-01-01T12:00:00"
  },
  "created_at": "2024-01-01T11:55:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

**状态说明**:
- `pending`: 等待处理
- `processing`: 正在处理
- `completed`: 处理完成
- `failed`: 处理失败

### 3. 模型管理接口

**GET** `/api/tender/models`

**功能**: 获取可用的模型列表和状态

**请求示例**:
```bash
curl "http://localhost:8082/api/tender/models"
```

**POST** `/api/tender/models/switch`

**功能**: 切换当前使用的模型

**请求示例**:
```bash
curl -X POST "http://localhost:8082/api/tender/models/switch" \
  -H "Content-Type: application/json" \
  -d '{
    "module_name": "tender_generation",
    "provider": "deepseek"
  }'
```

### 4. 健康检查接口

**GET** `/api/tender/health`

**功能**: 检查招标生成服务的健康状态

**请求示例**:
```bash
curl "http://localhost:8082/api/tender/health"
```

### 5. 任务管理接口

**GET** `/api/tender/tasks`

**功能**: 获取所有任务列表

**DELETE** `/api/tender/tasks/{task_id}`

**功能**: 删除指定任务

## 配置文件说明

### 1. 模型配置 (`config/model_config.json`)

```json
{
  "models": {
    "tender_notice": {
      "current": "ollama",
      "options": ["ollama", "deepseek"]
    },
    "tender_generation": {
      "current": "ollama",
      "options": ["ollama", "deepseek"]
    }
  },
  "providers": {
    "ollama": {
      "url": "http://localhost:11434",
      "model": "qwen2.5:7b"
    },
    "deepseek": {
      "api_key": "your_api_key_here",
      "base_url": "https://api.deepseek.com",
      "model": "deepseek-chat"
    }
  }
}
```

### 2. 招标生成配置 (`config/tender_generation_config.ini`)

```ini
[TextChunking]
ChunkSize = 2000
ChunkOverlap = 200
Separators = \n\n,\n,。,！,？,.,

[ModelSettings]
DefaultProvider = ollama
Timeout = 30
MaxRetries = 3

[TenderGeneration]
Sections = 第一章 采购公告,第二章 供应商须知,第三章 评审办法,第四章 合同条款及格式,第五章 采购人要求,第六章 响应文件格式
QualityLevel = standard
```

## 测试步骤

### 1. 基础功能测试

1. **检查服务状态**:
   ```bash
   curl "http://localhost:8082/api/tender/health"
   ```

2. **查看可用模型**:
   ```bash
   curl "http://localhost:8082/api/tender/models"
   ```

3. **上传文档生成招标书**:
   ```bash
   curl -X POST "http://localhost:8082/api/tender/generate" \
     -F "file=@test_document.pdf" \
     -F "model_provider=ollama"
   ```

4. **查询任务状态**:
   ```bash
   curl "http://localhost:8082/api/tender/status/{返回的task_id}"
   ```

### 2. 前端界面测试

访问 http://localhost:3000，使用Web界面进行测试：

1. 上传PDF或DOCX文档
2. 选择解析类型
3. 查看解析结果
4. 使用新增的招标文件生成功能（如果前端已集成）

### 3. API文档测试

访问 http://localhost:8082/docs，使用Swagger UI进行交互式测试：

1. 展开招标文件生成相关的API接口
2. 使用"Try it out"功能测试各个接口
3. 查看请求和响应的详细信息

## 依赖要求

### Python包依赖

确保安装以下依赖包：

```bash
pip install fastapi uvicorn
pip install python-docx PyMuPDF
pip install langchain-text-splitters
pip install requests
```

### 外部服务依赖

1. **Ollama服务** (本地模型):
   - 安装Ollama: https://ollama.ai/
   - 下载模型: `ollama pull qwen2.5:7b`
   - 启动服务: `ollama serve`

2. **DeepSeek API** (云端模型，可选):
   - 注册DeepSeek账号获取API Key
   - 在配置文件中设置API Key

## 故障排除

### 常见问题

1. **模型服务连接失败**:
   - 检查Ollama服务是否启动: `curl http://localhost:11434/api/tags`
   - 确认模型已下载: `ollama list`

2. **文档解析失败**:
   - 检查文件格式是否支持（PDF、DOCX）
   - 确认文件没有损坏
   - 查看服务器日志获取详细错误信息

3. **任务处理超时**:
   - 检查文档大小（建议小于50MB）
   - 调整配置文件中的超时设置
   - 考虑使用更强大的模型或硬件

### 日志查看

服务器日志会显示详细的处理过程和错误信息，包括：
- 文档解析进度
- 模型调用状态
- 错误堆栈信息

## 性能优化建议

1. **硬件要求**:
   - 推荐8GB以上内存
   - 使用SSD存储提高文件读写速度
   - GPU加速（如果使用本地大模型）

2. **配置优化**:
   - 根据文档大小调整分块参数
   - 设置合适的并发线程数
   - 使用更高性能的模型

3. **缓存策略**:
   - 考虑实现结果缓存
   - 使用Redis等持久化存储管理任务状态

## 扩展开发

### 添加新的模型提供商

1. 在`model_manager.py`中添加新的客户端初始化逻辑
2. 实现对应的API调用方法
3. 更新配置文件格式

### 自定义招标书模板

1. 修改`processor.py`中的章节定义
2. 调整提示词模板
3. 添加新的配置选项

### 集成到前端界面

1. 在前端添加招标文件生成功能模块
2. 实现文件上传和进度显示
3. 添加结果展示和下载功能