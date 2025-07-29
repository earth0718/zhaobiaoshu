# 招标书文档解析系统 API 文档

## 系统概述

招标书文档解析系统是一个基于 FastAPI 的文档处理和招标文件生成系统，提供文档解析、配置管理、招标生成、历史记录、过滤器和投标书生成等功能。

**系统信息：**
- 系统名称：招标书文档解析系统
- 版本：1.0.0
- 基础URL：`http://localhost:8000`
- API文档：`http://localhost:8000/docs`
- ReDoc文档：`http://localhost:8000/redoc`

## API 接口分类

### 1. 系统信息接口

#### 1.1 根路径
- **路径：** `GET /`
- **描述：** 系统欢迎页面
- **响应：**
```json
{
  "message": "欢迎使用招标书文档解析系统",
  "version": "1.0.0",
  "docs_url": "/docs",
  "api_info_url": "/api/info"
}
```

#### 1.2 API信息
- **路径：** `GET /api/info`
- **描述：** 获取API详细信息
- **响应：**
```json
{
  "system_name": "招标书文档解析系统",
  "version": "1.0.0",
  "features": {
    "document_parsing": "文档解析功能",
    "tender_generation": "招标文件生成",
    "history_management": "历史记录管理",
    "filter_processing": "智能过滤处理",
    "gender_book_generation": "投标书生成"
  },
  "supported_formats": {
    "input": ["pdf", "docx", "doc", "txt", "md"],
    "output": ["json", "docx", "md"]
  },
  "total_endpoints": 35,
  "modules": {
    "document_parsing": 7,
    "configuration_management": 5,
    "tender_generation": 9,
    "history_management": 6,
    "filter_processing": 1,
    "gender_book_generation": 8
  },
  "parser_info": {
    "name": "文档解析模块",
    "version": "1.0.0",
    "supported_formats": {
      ".pdf": "PDF文档",
      ".docx": "Word文档",
      ".doc": "Word文档",
      ".txt": "文本文件",
      ".md": "Markdown文件"
    }
  },
  "api_info": {
    "total_endpoints": 30,
    "modules": [
      "document_parsing",
      "configuration",
      "tender_generation",
      "history",
      "filter",
      "gender_book"
    ]
  }
}
```

#### 1.3 系统健康检查
- **路径：** `GET /health`
- **描述：** 系统整体健康状态检查
- **响应：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "api": "running",
    "document_parser": "running",
    "tender_generator": "running"
  }
}
```

#### 1.4 系统详细信息
- **路径：** `GET /info`
- **描述：** 获取系统详细信息和状态
- **响应：**
```json
{
  "system": {
    "name": "招标书文档解析系统",
    "version": "1.0.0",
    "status": "running"
  },
  "modules": {
    "document_parser": {
      "status": "active",
      "supported_formats": 5
    },
    "tender_generator": {
      "status": "active",
      "current_model": "ollama"
    },
    "history_manager": {
      "status": "active",
      "total_records": 0
    }
  },
  "api": {
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "total_endpoints": 30
  }
}
```

## 文档解析模块 (/api/parser)

### 1. 解析单个文档

**接口**: `POST /api/parser/parse`

**描述**: 上传并解析单个文档文件

**请求参数**:
- `file` (UploadFile): 要解析的文档文件
- `include_metadata` (bool, 可选): 是否包含元数据，默认 true
- `cleanup` (bool, 可选): 是否清理临时文件，默认 true
- `max_pages_per_batch` (int, 可选): PDF分页处理时每批处理的最大页数，默认 5，范围 1-20

**支持的文件格式**:
- PDF (.pdf)
- Word文档 (.docx, .doc)
- 文本文件 (.txt, .md)

**响应示例**:
```json
{
  "success": true,
  "message": "文档解析成功",
  "data": {
    "document_info": {
      "filename": "example.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "pages": 10
    },
    "content": [
      {
        "text": "文档内容",
        "type": "Title",
        "metadata": {}
      }
    ],
    "config": {
      "max_pages_per_batch": 5,
      "include_metadata": true
    }
  }
}
```

### 2. 批量解析文档

**接口**: `POST /api/parser/parse/batch`

**描述**: 批量上传并解析多个文档文件

**请求参数**:
- `files` (List[UploadFile]): 要解析的文档文件列表
- `include_metadata` (bool, 可选): 是否包含元数据，默认 true
- `cleanup` (bool, 可选): 是否清理临时文件，默认 true
- `max_pages_per_batch` (int, 可选): PDF分页处理时每批处理的最大页数，默认 5

### 3. 提取纯文本

**接口**: `POST /api/parser/extract/text`

**描述**: 从文档中提取纯文本内容

**请求参数**:
- `file` (UploadFile): 要提取文本的文档文件
- `max_length` (int, 可选): 最大文本长度限制

### 4. 提取结构化数据

**接口**: `POST /api/parser/extract/structured`

**描述**: 从文档中提取结构化数据，可以指定要提取的元素类型

**请求参数**:
- `file` (UploadFile): 要提取结构化数据的文档文件
- `target_types` (str, 可选): 目标元素类型，多个类型用逗号分隔，如: Title,Table,List

**常见的元素类型**:
- Title: 标题
- Header: 页眉
- Text: 正文
- Table: 表格
- List: 列表
- Image: 图片

### 5. 获取支持的文件格式

**接口**: `GET /api/parser/formats`

**描述**: 获取系统支持的所有文件格式信息

**响应示例**:
```json
{
  "supported_extensions": [".pdf", ".docx", ".doc", ".txt", ".md"],
  "supported_types": ["pdf", "docx", "doc", "txt", "md"],
  "format_mapping": {
    ".pdf": "pdf",
    ".docx": "docx",
    ".doc": "doc",
    ".txt": "txt",
    ".md": "md"
  },
  "total_formats": 5
}
```

### 6. 验证文件格式

**接口**: `GET /api/parser/validate/{filename}`

**描述**: 验证指定文件名的格式是否支持

**路径参数**:
- `filename` (str): 要验证的文件名

**响应示例**:
```json
{
  "filename": "example.pdf",
  "is_supported": true,
  "file_type": "pdf",
  "extension": ".pdf"
}
```

### 7. 解析器健康检查

**接口**: `GET /api/parser/health`

**描述**: 检查文档解析服务的健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "service": "文档解析服务",
  "version": "1.0.0",
  "supported_formats": 5,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 配置管理模块 (/api/config)

### 1. 获取解析器配置

**接口**: `GET /api/config/parser`

**描述**: 获取当前的解析器配置信息

**响应示例**:
```json
{
  "pdf_batch_config": {
    "max_pages_per_batch": 5
  },
  "parser_strategies": {
    "pdf": {
      "strategy": "auto",
      "include_page_breaks": true,
      "infer_table_structure": true
    }
  },
  "text_extraction_config": {
    "max_text_length": 1000000
  },
  "temp_file_config": {
    "auto_cleanup": true
  }
}
```

### 2. 获取文本提取配置

**接口**: `GET /api/config/parser/text-extraction`

**描述**: 获取文本提取相关配置

### 3. 获取支持的文件格式

**接口**: `GET /api/config/parser/supported-formats`

**描述**: 获取配置中支持的文件格式信息

**响应示例**:
```json
{
  "supported_extensions": [".pdf", ".docx", ".doc", ".txt", ".md"],
  "supported_types": ["pdf", "docx", "doc", "txt", "md"],
  "format_mapping": {
    ".pdf": "pdf",
    ".docx": "docx",
    ".doc": "doc",
    ".txt": "txt",
    ".md": "md"
  },
  "total_formats": 5
}
```

### 4. 更新解析器配置

**接口**: `PUT /api/config/parser/update`

**描述**: 更新解析器配置参数

**请求体**:
```json
{
  "max_pages_per_batch": 10,
  "pdf_strategy": "auto",
  "include_page_breaks": true,
  "infer_table_structure": true,
  "max_text_length": 2000000,
  "auto_cleanup": true
}
```

### 5. 重置解析器配置

**接口**: `POST /api/config/parser/reset`

**描述**: 将解析器配置重置为默认值

## 招标文件生成模块 (/api/tender)

### 1. 生成招标文件

**接口**: `POST /api/tender/generate`

**描述**: 上传文档并生成招标书，支持PDF和DOCX格式

**请求参数**:
- `file` (UploadFile): 要处理的文档文件（支持PDF、DOCX格式）
- `model_provider` (str, 可选): 模型提供商
- `quality_level` (str, 可选): 质量级别，默认"standard"

**响应示例**:
```json
{
  "task_id": "uuid-string",
  "message": "任务已创建，正在处理中...",
  "status_url": "/api/tender/status/uuid-string"
}
```

### 2. 从文本生成招标文件

**接口**: `POST /api/tender/generate_from_text`

**描述**: 根据用户输入的文本内容生成招标书

**请求体**:
```json
{
  "text_content": "招标项目描述文本",
  "model_provider": "ollama",
  "quality_level": "standard",
  "project_name": "招标项目",
  "include_sections": ["项目概述", "技术要求"],
  "custom_requirements": "特殊要求"
}
```

### 3. 查询任务状态

**接口**: `GET /api/tender/status/{task_id}`

**描述**: 查询招标文件生成任务的状态

**路径参数**:
- `task_id` (str): 任务ID

**响应示例**:
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "message": "任务完成",
  "result": {
    "word_file": {
      "filename": "tender_20240101_120000.docx",
      "download_url": "/api/tender/download/word/tender_20240101_120000.docx"
    },
    "markdown_file": {
      "filename": "tender_20240101_120000.md",
      "download_url": "/api/tender/download/markdown/tender_20240101_120000.md"
    }
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z"
}
```

### 4. 获取可用模型列表

**接口**: `GET /api/tender/models`

**描述**: 获取可用的AI模型列表和状态

**响应示例**:
```json
{
  "current_models": {
    "tender_generation": "ollama"
  },
  "available_providers": ["ollama", "openai"],
  "model_status": {
    "ollama": true,
    "openai": false
  }
}
```

### 5. 切换模型

**接口**: `POST /api/tender/models/switch`

**描述**: 切换当前使用的模型

**请求体**:
```json
{
  "module_name": "tender_generation",
  "provider": "ollama"
}
```

**响应示例**:
```json
{
  "message": "已切换 tender_generation 模块的模型到 ollama",
  "current_model": "ollama"
}
```

### 6. 招标生成服务健康检查

**接口**: `GET /api/tender/health`

**描述**: 检查招标生成服务的健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "model_manager": "running",
    "current_model": "ollama",
    "model_available": true
  },
  "active_tasks": 2
}
```

### 7. 获取所有任务列表

**接口**: `GET /api/tender/tasks`

**描述**: 获取所有招标文件生成任务的状态列表

**响应示例**:
```json
{
  "total_tasks": 10,
  "tasks": [
    {
      "task_id": "uuid-string",
      "status": "completed",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### 8. 删除任务

**接口**: `DELETE /api/tender/tasks/{task_id}`

**描述**: 删除指定的任务

**路径参数**:
- `task_id` (str): 任务ID

**响应示例**:
```json
{
  "message": "任务 uuid-string 已删除"
}
```

### 9. 下载生成的招标文件

**接口**: `GET /api/tender/download/{file_type}/{filename}`

**描述**: 下载生成的招标文件

**路径参数**:
- `file_type` (str): 文件类型，支持 'word' 或 'markdown'
- `filename` (str): 文件名

**文件类型说明**:
- `word`: Word文档格式 (.docx)
- `markdown`: Markdown格式 (.md)

**响应**: 文件下载流

## 历史记录模块 (/api/history)

### 1. 获取历史记录列表

**接口**: `GET /api/history/records`

**描述**: 获取招标文件生成历史记录列表，支持分页和过滤

**查询参数**:
- `limit` (int, 可选): 每页记录数，默认 20，范围 1-100
- `offset` (int, 可选): 偏移量，默认 0
- `status` (str, 可选): 状态过滤 (completed/failed)
- `model` (str, 可选): 模型过滤
- `date_from` (str, 可选): 开始日期 (ISO格式)
- `date_to` (str, 可选): 结束日期 (ISO格式)

**响应示例**:
```json
{
  "total": 100,
  "records": [
    {
      "record_id": "uuid-string",
      "task_id": "uuid-string",
      "status": "completed",
      "model_used": "ollama",
      "created_at": "2024-01-01T12:00:00Z",
      "completed_at": "2024-01-01T12:05:00Z",
      "processing_time": 300
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

### 2. 获取单个历史记录

**接口**: `GET /api/history/records/{record_id}`

**描述**: 根据记录ID获取单个历史记录详情

**路径参数**:
- `record_id` (str): 记录ID

### 3. 删除历史记录

**接口**: `DELETE /api/history/records/{record_id}`

**描述**: 删除指定的历史记录

**路径参数**:
- `record_id` (str): 记录ID

**响应示例**:
```json
{
  "message": "记录删除成功",
  "record_id": "uuid-string"
}
```

### 4. 获取历史记录统计

**接口**: `GET /api/history/statistics`

**描述**: 获取历史记录统计信息

**响应示例**:
```json
{
  "total_records": 100,
  "successful_records": 85,
  "failed_records": 15,
  "success_rate": 0.85,
  "most_used_model": "ollama",
  "average_processing_time": 280,
  "last_generation_time": "2024-01-01T12:00:00Z"
}
```

### 5. 导出历史记录

**接口**: `GET /api/history/export/{record_id}`

**描述**: 导出指定历史记录的详细信息

**路径参数**:
- `record_id` (str): 记录ID

**响应**: 导出的文件或数据

### 6. 清空所有历史记录

**接口**: `DELETE /api/history/records`

**描述**: 清空所有历史记录（不可逆操作）

**响应示例**:
```json
{
  "message": "已清空 100 条历史记录"
}
```

## 过滤器模块 (/api/filter)

### 1. 处理JSON文件过滤

**接口**: `POST /api/filter/process`

**描述**: 对JSON格式的文档内容进行智能过滤和优化处理，提高大模型理解效果

**请求体**: 任何JSON结构的数据

**响应示例**:
```json
{
  "success": true,
  "data": {
    "optimized_data": {
      "content": [
        {
          "type": "Title",
          "text": "项目概述",
          "section": "项目概述"
        }
      ]
    },
    "structured_text": "结构化文本内容",
    "llm_prompt": "适合大模型的提示词",
    "statistics": {
      "original_content_count": 100,
      "optimized_content_count": 85,
      "processing_time_seconds": 0.5,
      "optimization_ratio_percentage": 15.0
    }
  },
  "message": "JSON文件智能处理完成"
}
```

## 招标书生成模块 (/api/gender_book)

### 1. 生成投标书

**接口**: `POST /api/gender_book/generate_from_json`

**描述**: 从JSON格式的招标文档数据生成投标书

**请求体**:
```json
{
  "tender_document_json": {
    "content": [
      {
        "text": "项目概述",
        "type": "Title",
        "section": "项目概述"
      }
    ]
  },
  "model_name": "ollama",
  "batch_size": 5,
  "generate_outline_only": false
}
```

**响应示例**:
```json
{
  "success": true,
  "task_id": "uuid-string",
  "message": "投标书生成任务已创建"
}
```

### 2. 分析JSON内容

**接口**: `POST /api/gender_book/analyze_json`

**描述**: 分析JSON内容并返回章节计划，不生成具体内容

**请求体**:
```json
{
  "json_data": {
    "content": [
      {
        "text": "项目概述",
        "type": "Title",
        "section": "项目概述"
      }
    ]
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "JSON内容分析完成",
  "data": {
    "content_analysis": {
      "total_sections": 5,
      "key_topics": ["项目概述", "技术方案"]
    },
    "section_plan": {
      "sections": [
        {
          "title": "项目概述",
          "priority": "high"
        }
      ]
    }
  }
}
```

### 3. 查询任务状态

**接口**: `GET /api/gender_book/status/{task_id}`

**描述**: 查询投标书生成任务的状态

**路径参数**:
- `task_id` (str): 任务ID

**响应示例**:
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "message": "投标书生成完成",
  "result": {
    "bid_content": "生成的投标书内容",
    "sections_generated": 8,
    "total_pages": 25,
    "word_filename": "tender_20240101_120000_abc123.docx",
    "markdown_filename": "tender_20240101_120000_abc123.md"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z"
}
```

### 4. 获取标准章节模板

**接口**: `GET /api/gender_book/sections`

**描述**: 获取标准的投标书章节模板

**响应示例**:
```json
{
  "success": true,
  "sections": [
    {
      "id": "project_overview",
      "name": "项目概述",
      "description": "项目基本信息和背景介绍",
      "required": true
    },
    {
      "id": "technical_solution",
      "name": "技术方案",
      "description": "详细的技术实施方案",
      "required": true
    }
  ]
}
```

### 5. 获取任务列表

**接口**: `GET /api/gender_book/tasks`

**描述**: 获取所有投标书生成任务的列表，支持分页

**查询参数**:
- `limit` (int, 可选): 每页记录数，默认 20
- `offset` (int, 可选): 偏移量，默认 0

**响应示例**:
```json
{
  "success": true,
  "total": 5,
  "tasks": [
    {
      "task_id": "uuid-string",
      "status": "completed",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:05:00Z"
    }
  ],
  "has_more": false
}
```

### 6. 删除任务

**接口**: `DELETE /api/gender_book/tasks/{task_id}`

**描述**: 删除指定的投标书生成任务

**路径参数**:
- `task_id` (str): 任务ID

**响应示例**:
```json
{
  "success": true,
  "message": "任务删除成功",
  "task_id": "uuid-string"
}
```

### 7. 下载生成的文件

**接口**: `GET /api/gender_book/download/{file_type}/{filename}`

**描述**: 下载生成的投标书文件

**路径参数**:
- `file_type` (str): 文件类型，支持 'word' 或 'markdown'
- `filename` (str): 文件名

**文件类型说明**:
- `word`: Word文档格式 (.docx)
- `markdown`: Markdown格式 (.md)

**响应**: 文件下载流

### 8. 投标书生成模块健康检查

**接口**: `GET /api/gender_book/health`

**描述**: 检查投标书生成模块的健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "module": "gender_book",
  "message": "投标书生成模块运行正常",
  "features": {
    "section_manager": "available",
    "content_analysis": "available",
    "section_planning": "available"
  },
  "active_tasks": 2,
  "standard_sections_count": 12
}
```



## 静态文件服务

### 1. 前端静态文件

**路径**: `/static/*`

**描述**: 提供前端静态文件服务（如果frontend目录存在）

### 2. 配置文件访问

**路径**: `/config/*`

**描述**: 提供配置文件的静态访问服务

## 错误响应格式

所有API接口在发生错误时都会返回统一的错误响应格式：

```json
{
  "detail": "错误描述信息",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

常见的HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `422`: 请求数据验证失败
- `500`: 服务器内部错误

## 使用示例

### 1. 解析文档示例

```bash
# 上传并解析PDF文档
curl -X POST "http://localhost:8000/api/parser/parse" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "include_metadata=true" \
  -F "max_pages_per_batch=5"
```

### 2. 生成招标文件示例

```bash
# 生成招标文件
curl -X POST "http://localhost:8000/api/tender/generate" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@source_document.pdf" \
  -F "model=ollama"

# 查询任务状态
curl -X GET "http://localhost:8000/api/tender/status/{task_id}"

# 下载生成的Word文件
curl -X GET "http://localhost:8000/api/tender/download/word/tender_20240101_120000.docx" \
  --output tender.docx
```

### 3. 查询历史记录示例

```bash
# 获取历史记录列表
curl -X GET "http://localhost:8000/api/history/records?limit=10&status=completed"

# 获取统计信息
curl -X GET "http://localhost:8000/api/history/statistics"
```

## 注意事项

1. **文件上传限制**: 系统对上传文件的大小和类型有限制，请确保文件符合要求
2. **任务处理时间**: 招标文件生成是异步处理，处理时间取决于文档复杂度和模型性能
3. **文件存储**: 生成的文件会保存在服务器的download目录中，建议定期清理
4. **API限流**: 生产环境建议配置适当的API限流策略
5. **安全性**: 生产环境需要配置适当的CORS策略和身份验证机制

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持PDF、Word、文本文件解析
- 支持招标文件生成
- 支持历史记录管理
- 支持配置管理
- 支持健康检查
- 支持文件下载功能