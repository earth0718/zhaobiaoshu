# 多文件招标书生成功能使用指南

## 功能概述

多文件招标书生成功能允许用户同时上传多个文档文件（PDF、DOCX），系统会将这些文件的内容合并处理，生成一份完整的招标书文档。

### 处理流程

```
文件1.pdf + 文件2.docx + 文件3.pdf → 内容解析 → 内容合并 → 优化处理 → 生成完整招标书（6个章节）
```

## API接口

### 多文件上传接口

**接口地址：** `POST /generate_multiple`

**请求参数：**
- `files`: 上传的文件列表（支持PDF、DOCX格式）
- `model_provider`: 模型提供商（可选）
- `quality_level`: 质量等级（可选）
- `project_name`: 项目名称（可选）
- `custom_requirements`: 自定义要求（可选）

**响应格式：**
```json
{
    "task_id": "生成的任务ID",
    "message": "任务已提交，正在后台处理",
    "estimated_time": "预估处理时间（分钟）"
}
```

### 任务状态查询

使用现有的 `/status/{task_id}` 接口查询处理状态。

## 配置说明

### 配置文件位置

- 主配置文件：`config/multi_file_config.ini`
- 示例配置：`config/multi_file_config.example.ini`

### 主要配置项

#### 文件限制
```ini
[files]
# 最大文件数量
max_files = 10

# 单个文件最大大小（MB）
max_file_size_mb = 50

# 支持的文件格式
supported_formats = .pdf,.docx
```

#### 性能优化
```ini
[performance]
# 启用内容去重
enable_deduplication = true

# 相似度检测阈值
similarity_threshold = 0.8

# 启用缓存
enable_caching = true
```

#### 输出设置
```ini
[output]
# 输出目录
markdown_output_dir = download/markdown
word_output_dir = download/word

# 默认项目名称
default_project_name = 多文件招标项目
```

## 使用示例

### Python客户端示例

```python
import requests
import time

# 上传多个文件
files = [
    ('files', ('项目需求.pdf', open('项目需求.pdf', 'rb'), 'application/pdf')),
    ('files', ('技术规范.docx', open('技术规范.docx', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')),
    ('files', ('预算说明.pdf', open('预算说明.pdf', 'rb'), 'application/pdf'))
]

data = {
    'project_name': '智慧城市建设项目',
    'quality_level': 'high',
    'custom_requirements': '请重点关注技术可行性和成本控制'
}

# 提交任务
response = requests.post('http://localhost:8000/generate_multiple', files=files, data=data)
result = response.json()
task_id = result['task_id']

print(f"任务已提交，ID: {task_id}")

# 查询状态
while True:
    status_response = requests.get(f'http://localhost:8000/status/{task_id}')
    status = status_response.json()
    
    print(f"当前状态: {status['status']}")
    
    if status['status'] == 'completed':
        print("处理完成！")
        print(f"下载链接: {status.get('download_urls', {})}")
        break
    elif status['status'] == 'failed':
        print(f"处理失败: {status.get('error', '未知错误')}")
        break
    
    time.sleep(10)  # 等待10秒后再次查询
```

### cURL示例

```bash
# 上传多个文件
curl -X POST "http://localhost:8000/generate_multiple" \
  -F "files=@项目需求.pdf" \
  -F "files=@技术规范.docx" \
  -F "files=@预算说明.pdf" \
  -F "project_name=智慧城市建设项目" \
  -F "quality_level=high"
```

## 性能优化功能

### 内容去重
- 自动检测并移除重复的文档内容
- 基于文本哈希值进行快速去重

### 相似度检测
- 识别相似的文档段落
- 合并相似内容，避免冗余

### 缓存机制
- 缓存处理结果，提高重复处理效率
- 支持配置缓存大小限制

### 并发处理
- 支持多文档并行解析
- 可配置最大并发任务数

## 错误处理

### 常见错误及解决方案

1. **文件格式不支持**
   - 错误信息："文件格式不支持"
   - 解决方案：确保上传的文件为PDF或DOCX格式

2. **文件数量超限**
   - 错误信息："最多支持同时上传X个文件"
   - 解决方案：减少上传文件数量或修改配置文件中的max_files设置

3. **文件大小超限**
   - 错误信息："文件大小超过限制"
   - 解决方案：压缩文件或修改配置文件中的max_file_size_mb设置

4. **内容解析失败**
   - 错误信息："文档解析失败"
   - 解决方案：检查文件是否损坏，或尝试重新保存文件

### 错误恢复

- 系统支持部分文件处理失败时继续处理其他文件
- 可通过配置文件设置是否在错误时继续处理
- 支持自动重试机制

## 最佳实践

1. **文件准备**
   - 确保文件内容清晰、格式规范
   - 避免上传过大的文件（建议单个文件不超过20MB）
   - 文件名使用有意义的名称

2. **配置优化**
   - 根据服务器性能调整并发处理数量
   - 合理设置缓存大小，平衡内存使用和性能
   - 定期清理输出目录，避免磁盘空间不足

3. **监控和维护**
   - 定期检查日志文件，及时发现问题
   - 监控系统资源使用情况
   - 备份重要的配置文件

## 技术架构

### 核心模块

- `batch_processor.py`: 批量文档处理核心
- `performance_optimizer.py`: 性能优化模块
- `multi_file_settings.py`: 配置管理模块
- `api.py`: REST API接口

### 处理流程

1. **文件上传和验证**
2. **并行文档解析**
3. **内容合并和优化**
4. **招标书生成**
5. **结果保存和返回**

### 扩展性

- 支持添加新的文件格式解析器
- 可扩展性能优化算法
- 支持自定义招标书模板
- 可集成外部存储服务