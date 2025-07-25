# 招标书生成历史记录模块

## 功能概述

本模块提供招标书生成的历史记录管理功能，自动保存最近20条生成记录，支持查询、统计和导出功能。

## 主要特性

- ✅ 自动保存招标书生成历史
- ✅ 限制保存最近20条记录
- ✅ 支持成功和失败记录
- ✅ 提供详细的统计信息
- ✅ 支持历史记录导出
- ✅ 支持多种过滤和查询条件

## API接口文档

### 1. 获取历史记录列表

**接口地址：** `GET /api/history/records`

**功能说明：** 获取招标书生成历史记录列表，支持分页和多种过滤条件

**请求参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| limit | int | 否 | 20 | 每页记录数 (1-100) |
| offset | int | 否 | 0 | 偏移量 |
| status | string | 否 | - | 状态过滤 (completed/failed) |
| model | string | 否 | - | 模型过滤 |
| date_from | string | 否 | - | 开始日期 (ISO格式) |
| date_to | string | 否 | - | 结束日期 (ISO格式) |

**请求示例：**
```bash
GET /api/history/records?limit=10&status=completed&model=ollama
```

**响应示例：**
```json
{
  "total_count": 15,
  "records": [
    {
      "record_id": "uuid-string",
      "task_id": "task-uuid",
      "original_filename": "document.pdf",
      "file_size": 1024000,
      "model_provider": "ollama",
      "quality_level": "standard",
      "generation_time": "2024-01-01T12:00:00",
      "processing_duration": 45.2,
      "status": "completed",
      "error_message": null,
      "tender_content": "招标书内容...",
      "tender_summary": "招标书摘要...",
      "created_at": "2024-01-01T12:00:00",
      "file_path": "/path/to/content/file.txt"
    }
  ],
  "has_more": true
}
```

### 2. 获取单个历史记录

**接口地址：** `GET /api/history/records/{record_id}`

**功能说明：** 根据记录ID获取单个历史记录详情

**路径参数：**
- `record_id`: 记录ID

**响应示例：**
```json
{
  "record_id": "uuid-string",
  "task_id": "task-uuid",
  "original_filename": "document.pdf",
  "file_size": 1024000,
  "model_provider": "ollama",
  "quality_level": "standard",
  "generation_time": "2024-01-01T12:00:00",
  "processing_duration": 45.2,
  "status": "completed",
  "error_message": null,
  "tender_content": "完整的招标书内容...",
  "tender_summary": "招标书摘要...",
  "created_at": "2024-01-01T12:00:00",
  "file_path": "/path/to/content/file.txt"
}
```

### 3. 删除历史记录

**接口地址：** `DELETE /api/history/records/{record_id}`

**功能说明：** 删除指定的历史记录

**路径参数：**
- `record_id`: 记录ID

**响应示例：**
```json
{
  "message": "记录删除成功",
  "record_id": "uuid-string"
}
```

### 4. 获取历史记录统计

**接口地址：** `GET /api/history/statistics`

**功能说明：** 获取历史记录统计信息

**响应示例：**
```json
{
  "total_records": 20,
  "completed_count": 18,
  "failed_count": 2,
  "most_used_model": "ollama",
  "average_processing_time": 42.5,
  "latest_generation": "2024-01-01T12:00:00"
}
```

### 5. 清空所有历史记录

**接口地址：** `DELETE /api/history/records`

**功能说明：** 清空所有历史记录（不可逆操作）

**响应示例：**
```json
{
  "message": "已清空 20 条历史记录"
}
```

### 6. 导出历史记录

**接口地址：** `GET /api/history/export/{record_id}`

**功能说明：** 导出指定历史记录的招标书内容

**路径参数：**
- `record_id`: 记录ID

**响应：** 返回文本文件下载

## 数据模型

### TenderHistoryRecord

| 字段名 | 类型 | 说明 |
|--------|------|------|
| record_id | string | 记录唯一ID |
| task_id | string | 任务ID |
| original_filename | string | 原始文件名 |
| file_size | int | 文件大小（字节） |
| model_provider | string | 模型提供商 |
| quality_level | string | 质量级别 |
| generation_time | string | 生成时间 |
| processing_duration | float | 处理耗时（秒） |
| status | string | 状态 (completed/failed) |
| error_message | string | 错误信息（失败时） |
| tender_content | string | 招标书内容 |
| tender_summary | string | 招标书摘要 |
| created_at | string | 创建时间 |
| file_path | string | 内容文件路径 |

## 存储机制

### 文件结构
```
src/history/
├── records.json          # 记录索引文件
└── content/             # 内容存储目录
    ├── {record_id}.txt  # 招标书内容文件
    └── ...
```

### 自动清理
- 自动保持最近20条记录
- 超出限制的记录会被自动删除
- 删除记录时同时清理对应的内容文件

## 使用示例

### Python客户端示例

```python
import requests

# 获取历史记录列表
response = requests.get('http://localhost:8000/api/history/records')
history_data = response.json()

print(f"总记录数: {history_data['total_count']}")
for record in history_data['records']:
    print(f"文件: {record['original_filename']}, 状态: {record['status']}")

# 获取统计信息
stats = requests.get('http://localhost:8000/api/history/statistics').json()
print(f"成功率: {stats['completed_count'] / stats['total_records'] * 100:.1f}%")

# 导出特定记录
record_id = "your-record-id"
response = requests.get(f'http://localhost:8000/api/history/export/{record_id}')
with open('exported_tender.txt', 'w', encoding='utf-8') as f:
    f.write(response.text)
```

### JavaScript客户端示例

```javascript
// 获取历史记录
fetch('/api/history/records?limit=10')
  .then(response => response.json())
  .then(data => {
    console.log('历史记录:', data.records);
  });

// 获取统计信息
fetch('/api/history/statistics')
  .then(response => response.json())
  .then(stats => {
    console.log('统计信息:', stats);
  });
```

## 注意事项

1. **存储限制**：系统只保存最近20条记录，超出的记录会被自动删除
2. **文件管理**：删除记录时会同时删除对应的内容文件
3. **错误处理**：历史记录保存失败不会影响招标书生成的主流程
4. **性能考虑**：大量历史记录查询时建议使用分页参数
5. **数据安全**：清空操作不可逆，请谨慎使用

## 集成说明

历史记录模块已自动集成到招标书生成流程中：
- 每次招标书生成完成后自动保存记录
- 包括成功和失败的生成尝试
- 记录详细的处理时间和错误信息
- 支持不同模型和质量级别的记录