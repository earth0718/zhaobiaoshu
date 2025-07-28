# 招标书生成模块 API 接口文档

## 概述

招标书生成模块（gender_book）是一个专门用于处理经过 filter.py 过滤器处理后的 JSON 数据，并生成完整招标书的模块。该模块特别针对小模型（如 deepseek 和 qwen2.5:7b）进行了优化，采用分章节生成的策略来确保生成质量。

## 核心功能

1. **智能章节分析**: 分析过滤后的 JSON 数据，自动生成招标书章节结构
2. **分章节生成**: 针对小模型优化，分批次生成招标书内容
3. **异步处理**: 支持大文档的异步处理，避免超时
4. **任务管理**: 完整的任务状态跟踪和管理
5. **灵活配置**: 支持只生成大纲或完整内容

## API 接口列表

### 1. 从 JSON 数据生成招标书

**接口地址**: `POST /api/gender_book/generate_from_json`

**功能描述**: 接收经过 filter.py 处理的 JSON 数据，生成完整的招标书

**请求参数**:
```json
{
  "json_data": {},  // 必需，经过filter.py处理的JSON数据
  "outline_only": false,  // 可选，是否只生成大纲，默认false
  "model_provider": "deepseek",  // 可选，模型提供商，默认deepseek
  "quality_level": "standard"  // 可选，生成质量级别，默认standard
}
```

**响应示例**:
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "message": "招标书生成任务已启动",
  "estimated_time": "预计需要5-10分钟"
}
```

### 2. 上传 JSON 文件生成招标书

**接口地址**: `POST /api/gender_book/upload_json`

**功能描述**: 上传 JSON 文件来生成招标书

**请求参数**:
- `file`: JSON 文件（multipart/form-data）
- `outline_only`: 是否只生成大纲（可选）
- `model_provider`: 模型提供商（可选）
- `quality_level`: 生成质量级别（可选）

**响应示例**:
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "message": "文件上传成功，招标书生成任务已启动",
  "file_info": {
    "filename": "filtered_data.json",
    "size": 1024576
  }
}
```

### 3. 查询任务状态

**接口地址**: `GET /api/gender_book/status/{task_id}`

**功能描述**: 查询特定招标书生成任务的状态

**路径参数**:
- `task_id`: 任务ID

**响应示例**:
```json
{
  "task_id": "uuid-string",
  "status": "completed",  // processing, completed, failed
  "progress": 100,
  "current_step": "文档组装完成",
  "result": {
    "tender_content": "完整的招标书内容...",
    "sections": [
      {
        "title": "项目概述",
        "content": "项目概述内容..."
      }
    ],
    "statistics": {
      "total_sections": 8,
      "total_words": 15000,
      "generation_time": "8分32秒"
    }
  },
  "error": null
}
```

### 4. 获取所有任务状态

**接口地址**: `GET /api/gender_book/tasks`

**功能描述**: 获取所有招标书生成任务的状态列表

**响应示例**:
```json
{
  "tasks": [
    {
      "task_id": "uuid-string-1",
      "status": "completed",
      "created_at": "2024-01-01T10:00:00Z",
      "completed_at": "2024-01-01T10:08:32Z"
    },
    {
      "task_id": "uuid-string-2",
      "status": "processing",
      "created_at": "2024-01-01T11:00:00Z",
      "progress": 60
    }
  ],
  "total": 2
}
```

### 5. 删除任务记录

**接口地址**: `DELETE /api/gender_book/tasks/{task_id}`

**功能描述**: 删除指定的任务记录

**路径参数**:
- `task_id`: 任务ID

**响应示例**:
```json
{
  "message": "任务记录已删除",
  "task_id": "uuid-string"
}
```

### 6. 分析 JSON 内容

**接口地址**: `POST /api/gender_book/analyze_json`

**功能描述**: 分析 JSON 内容并返回章节计划，不实际生成招标书

**请求参数**:
```json
{
  "json_data": {}  // 必需，要分析的JSON数据
}
```

**响应示例**:
```json
{
  "analysis_result": {
    "project_type": "工程建设",
    "key_info": {
      "project_name": "某某工程项目",
      "budget_range": "1000-5000万元",
      "timeline": "12个月"
    },
    "sections_plan": [
      {
        "title": "项目概述",
        "priority": "high",
        "estimated_tokens": 800,
        "content_sources": ["项目基本信息", "建设规模"]
      },
      {
        "title": "采购公告",
        "priority": "high",
        "estimated_tokens": 600,
        "content_sources": ["采购信息", "公告要求"]
      }
    ],
    "total_estimated_tokens": 5200
  }
}
```

### 7. 健康检查

**接口地址**: `GET /api/gender_book/health`

**功能描述**: 检查招标书生成模块的健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "module": "gender_book",
  "version": "1.0.0",
  "dependencies": {
    "llm_service": "available",
    "section_manager": "available",
    "tender_generator": "available"
  },
  "active_tasks": 2,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 8. 获取标准章节模板

**接口地址**: `GET /api/gender_book/sections`

**功能描述**: 获取预定义的标准招标书章节模板

**响应示例**:
```json
{
  "standard_sections": [
    {
      "id": "project_overview",
      "title": "项目概述",
      "description": "项目基本信息、建设规模、技术要求等",
      "priority": "high",
      "typical_content": ["项目名称", "建设地点", "建设规模", "技术标准"]
    },
    {
      "id": "procurement_announcement",
      "title": "采购公告",
      "description": "采购项目基本信息和公告内容",
      "priority": "high",
      "typical_content": ["采购项目名称", "采购方式", "预算金额", "采购需求"]
    }
  ]
}
```

## 使用流程

### 标准流程

1. **准备数据**: 使用 filter.py 处理原始文档，获得优化后的 JSON 数据
2. **提交生成任务**: 调用 `/api/gender_book/generate_from_json` 接口
3. **监控进度**: 定期调用 `/api/gender_book/status/{task_id}` 查询状态
4. **获取结果**: 任务完成后从状态接口获取生成的招标书内容

### 文件上传流程

1. **上传文件**: 调用 `/api/gender_book/upload_json` 接口上传 JSON 文件
2. **监控进度**: 同标准流程
3. **获取结果**: 同标准流程

### 预分析流程

1. **分析内容**: 调用 `/api/gender_book/analyze_json` 接口分析 JSON 数据
2. **查看计划**: 根据分析结果决定是否继续生成
3. **执行生成**: 如果满意分析结果，再调用生成接口

## 错误处理

### 常见错误码

- `400`: 请求参数错误
- `404`: 任务不存在
- `422`: 数据验证失败
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "error": "错误类型",
  "message": "详细错误信息",
  "detail": "技术细节（开发模式下）"
}
```

## 性能优化

### 针对小模型的优化策略

1. **分章节处理**: 将大文档拆分为多个章节，分别生成
2. **上下文管理**: 为每个章节提供精确的上下文信息
3. **Token 控制**: 严格控制每次请求的 token 数量
4. **批次生成**: 支持分批次生成，避免超时

### 建议的使用方式

1. **大文档**: 建议使用 `outline_only=true` 先生成大纲，确认后再生成完整内容
2. **小模型**: 推荐使用 deepseek 或 qwen2.5:7b，已针对这些模型进行优化
3. **质量控制**: 可以通过 `quality_level` 参数调整生成质量和速度的平衡

## 配置说明

### 模型提供商

- `deepseek`: DeepSeek 模型（推荐）
- `qwen`: Qwen2.5:7b 模型（推荐）
- 其他模型需要在 LLM 服务中配置

### 质量级别

- `fast`: 快速生成，适合预览
- `standard`: 标准质量（默认）
- `high`: 高质量生成，耗时较长

## 注意事项

1. **数据格式**: 确保输入的 JSON 数据是经过 filter.py 处理的格式
2. **异步处理**: 大文档生成是异步的，需要轮询状态接口获取结果
3. **资源管理**: 建议定期清理已完成的任务记录
4. **错误重试**: 如果生成失败，可以重新提交任务

## 示例代码

### Python 客户端示例

```python
import requests
import json
import time

# 1. 提交生成任务
with open('filtered_data.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

response = requests.post('http://localhost:8000/api/gender_book/generate_from_json', 
                        json={
                            'json_data': json_data,
                            'model_provider': 'deepseek',
                            'quality_level': 'standard'
                        })

task_info = response.json()
task_id = task_info['task_id']
print(f"任务已提交，ID: {task_id}")

# 2. 监控任务状态
while True:
    status_response = requests.get(f'http://localhost:8000/api/gender_book/status/{task_id}')
    status_data = status_response.json()
    
    print(f"当前状态: {status_data['status']}, 进度: {status_data.get('progress', 0)}%")
    
    if status_data['status'] == 'completed':
        print("招标书生成完成！")
        tender_content = status_data['result']['tender_content']
        # 保存结果
        with open('generated_tender.txt', 'w', encoding='utf-8') as f:
            f.write(tender_content)
        break
    elif status_data['status'] == 'failed':
        print(f"生成失败: {status_data.get('error', '未知错误')}")
        break
    
    time.sleep(10)  # 等待10秒后再次查询
```

### JavaScript 客户端示例

```javascript
// 1. 提交生成任务
async function generateTender(jsonData) {
    const response = await fetch('/api/gender_book/generate_from_json', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            json_data: jsonData,
            model_provider: 'deepseek',
            quality_level: 'standard'
        })
    });
    
    const taskInfo = await response.json();
    return taskInfo.task_id;
}

// 2. 监控任务状态
async function monitorTask(taskId) {
    while (true) {
        const response = await fetch(`/api/gender_book/status/${taskId}`);
        const statusData = await response.json();
        
        console.log(`状态: ${statusData.status}, 进度: ${statusData.progress || 0}%`);
        
        if (statusData.status === 'completed') {
            console.log('招标书生成完成！');
            return statusData.result.tender_content;
        } else if (statusData.status === 'failed') {
            throw new Error(`生成失败: ${statusData.error || '未知错误'}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 10000)); // 等待10秒
    }
}
```