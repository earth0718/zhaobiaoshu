# 招标书文档解析系统

基于 `unstructured` 库的文档解析系统，支持 PDF、Word、TXT 等多种格式的文件解析，并将解析结果转换为 JSON 格式。

## 功能特性

- 📄 **多格式支持**: 支持 PDF、Word (.docx/.doc)、TXT、Markdown 等格式
- 🔍 **智能解析**: 自动识别文档结构，提取标题、段落、表格、列表等元素
- 📊 **结构化输出**: 将解析结果转换为标准 JSON 格式
- 🚀 **高性能**: 支持单文件和批量文件处理
- 🛠️ **灵活配置**: 可选择包含元数据、指定提取类型等
- 🌐 **RESTful API**: 提供完整的 HTTP API 接口
- 📚 **详细文档**: 完整的 API 文档和使用示例

## 项目结构

```
zhaobiaoshu/
├── README.md                 # 项目说明文档
├── API_DOCUMENTATION.md      # API 接口文档
├── requirements.txt          # 项目依赖
├── main.py                  # 主应用入口
├── config/                  # 配置文件目录
│   └── __init__.py
└── src/
    └── parser/              # 文档解析模块
        ├── __init__.py      # 模块初始化
        ├── document_parser.py    # 核心解析器
        ├── document_service.py   # 业务服务层
        ├── api.py               # API 接口
        └── example.py           # 使用示例
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- pip 包管理器

### 2. 安装依赖

```bash
# 克隆项目（如果从 Git 仓库）
git clone <repository-url>
cd zhaobiaoshu

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动服务

```bash
# 开发环境启动
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问服务

- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **系统信息**: http://localhost:8000/

## 使用示例

### API 调用示例

#### 解析单个文档

```bash
curl -X POST "http://localhost:8000/api/v1/document/parse" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### 提取纯文本

```bash
curl -X POST "http://localhost:8000/api/v1/document/extract/text" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### 批量处理

```bash
curl -X POST "http://localhost:8000/api/v1/document/parse/batch" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx"
```

### Python 代码示例

```python
from src.parser import DocumentParser, get_document_service

# 使用核心解析器
parser = DocumentParser()
result = parser.parse_to_json('document.pdf')
print(f"解析了 {result['document_info']['total_elements']} 个元素")

# 使用服务层
service = get_document_service()
with open('document.pdf', 'rb') as f:
    file_content = f.read()
    result = service.parse_uploaded_file(file_content, 'document.pdf')
```

## 支持的文件格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| PDF | .pdf | 支持文本、表格、图像提取 |
| Word | .docx, .doc | Microsoft Word 文档 |
| 文本 | .txt | 纯文本文件 |
| Markdown | .md | Markdown 格式文件 |

## API 接口概览

### 核心接口

- `POST /api/v1/document/parse` - 解析单个文档
- `POST /api/v1/document/parse/batch` - 批量解析文档
- `POST /api/v1/document/extract/text` - 提取纯文本
- `POST /api/v1/document/extract/structured` - 提取结构化数据

### 工具接口

- `GET /api/v1/document/formats` - 获取支持的格式
- `GET /api/v1/document/validate/{filename}` - 验证文件格式
- `GET /api/v1/document/health` - 健康检查

详细的 API 文档请参考 [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 配置说明

### 解析器配置

```python
# 在 document_parser.py 中可以调整解析配置
parser_config = {
    'pdf': {
        'strategy': 'auto',  # 解析策略: auto, fast, ocr_only, hi_res
        'include_page_breaks': True,
        'infer_table_structure': True
    },
    'docx': {
        'include_page_breaks': True,
        'infer_table_structure': True
    }
}
```

### 服务配置

```python
# 在 main.py 中可以调整服务配置
DEFAULT_CONFIG = {
    'temp_dir': None,  # 临时文件目录
    'cleanup_temp_files': True,  # 自动清理临时文件
    'max_file_size': 50 * 1024 * 1024,  # 最大文件大小 50MB
}
```

## 开发指南

### 项目架构

1. **document_parser.py**: 核心解析器，直接使用 unstructured 库
2. **document_service.py**: 业务服务层，处理文件上传、临时文件管理等
3. **api.py**: RESTful API 接口层
4. **main.py**: FastAPI 应用入口

### 扩展开发

#### 添加新的文件格式支持

1. 在 `DocumentParser.SUPPORTED_EXTENSIONS` 中添加新格式
2. 在 `parse_document` 方法中添加对应的解析逻辑
3. 更新文档和测试

#### 添加新的 API 接口

1. 在 `api.py` 中添加新的路由函数
2. 定义相应的 Pydantic 模型
3. 更新 API 文档

### 测试

```bash
# 运行示例脚本
python src/parser/example.py

# 测试 API 接口
curl http://localhost:8000/api/v1/document/health
```

## 部署

### 开发环境

```bash
python main.py
```

### 生产环境

```bash
# 使用 Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用 Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker 部署

```dockerfile
# Dockerfile 示例
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 性能优化

### 建议配置

- **文件大小限制**: 建议单文件不超过 10MB
- **并发处理**: 建议同时处理文件数不超过 10 个
- **内存管理**: 及时清理临时文件
- **缓存策略**: 可考虑对解析结果进行缓存

### 监控指标

- 文件解析成功率
- 平均解析时间
- 内存使用情况
- 临时文件清理状态

## 故障排除

### 常见问题

1. **依赖安装失败**
   - 确保 Python 版本 >= 3.8
   - 使用虚拟环境安装依赖
   - 检查网络连接

2. **PDF 解析失败**
   - 确保安装了 PDF 相关依赖
   - 检查 PDF 文件是否损坏
   - 尝试不同的解析策略

3. **内存不足**
   - 减少并发处理数量
   - 及时清理临时文件
   - 增加系统内存

4. **API 响应慢**
   - 检查文件大小
   - 优化解析配置
   - 考虑异步处理

### 日志查看

```bash
# 查看应用日志
tail -f app.log

# 查看错误日志
grep ERROR app.log
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 更新日志

### v1.0.0 (2024-01-01)

- ✨ 初始版本发布
- 📄 支持 PDF、Word、TXT 文件解析
- 🌐 提供完整的 RESTful API
- 📚 完整的文档和示例
- 🚀 支持批量处理
- 🛠️ 灵活的配置选项

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目 Issues
- 邮箱: [your-email@example.com]
- 文档: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

**项目状态**: 🟢 活跃开发中  
**版本**: 1.0.0  
**最后更新**: 2024-01-01