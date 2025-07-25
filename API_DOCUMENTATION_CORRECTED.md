# 招标书文档解析系统 API 文档（修正版）

## 概述

招标书文档解析系统是一个基于 `unstructured` 库的文档解析服务，支持 PDF、Word、TXT 等多种格式的文件解析，并将解析结果转换为 JSON 格式。

## 发现的问题和修正

### 主要问题

1. **API路径不一致**：
   - 问题：API实现中使用的是 `/api/documents`，但文档中写的是 `/api/v1/document`
   - 修正：已将API实现中的路径前缀修改为 `/api/v1/document`

2. **缺少cleanup参数**：
   - 问题：API文档中提到了 `cleanup` 参数，但实际API实现中没有暴露这个参数
   - 修正：已在 `/parse` 和 `/parse/batch` 接口中添加了 `cleanup` 参数

3. **URL拼写错误**：
   - 问题：文档中有一处写成了 `/api/v1/documents/parse`（多了一个s）
   - 修正：应该是 `/api/v1/document/parse`

## 基本信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v1
- **API前缀**: `/api/v1/document`
- **文档地址**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc地址**: `http://localhost:8000/redoc`

## 支持的文件格式

| 扩展名 | 文件类型 | 说明 |
|--------|----------|------|
| .pdf | PDF文档 | 支持文本、图像、表格提取 |
| .docx | Word文档 | 现代Word格式 |
| .doc | Word文档 | 旧版Word格式 |
| .txt | 纯文本文件 | 普通文本文件 |
| .md | Markdown文件 | Markdown格式文本 |

## API 接口详情

### 1. 系统信息接口

#### 1.1 获取系统根信息

**接口地址**: `GET /`

**描述**: 获取系统基本信息和可用接口列表

#### 1.2 健康检查

**接口地址**: `GET /health`

**描述**: 检查系统运行状态

#### 1.3 获取详细系统信息

**接口地址**: `GET /info`

**描述**: 获取系统详细信息，包括功能特性和支持格式

### 2. 文档解析接口

#### 2.1 解析单个文档

**接口地址**: `POST /api/v1/document/parse`

**描述**: 解析单个文档文件并返回JSON格式的结果

**请求参数**:
- `file` (文件): 要解析的文档文件 (必需)
- `include_metadata` (查询参数): 是否包含元数据，默认为 `true`
- `cleanup` (查询参数): 是否清理临时文件，默认为 `true`
- `max_pages_per_batch` (查询参数): PDF分页处理时每批处理的最大页数，默认为 `5`，范围 1-20

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/document/parse?include_metadata=true&cleanup=true&max_pages_per_batch=5" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### 2.2 批量解析文档

**接口地址**: `POST /api/v1/document/parse/batch`

**描述**: 批量解析多个文档文件

**请求参数**:
- `files` (文件列表): 要解析的文档文件列表 (必需)
- `include_metadata` (查询参数): 是否包含元数据，默认为 `true`
- `cleanup` (查询参数): 是否清理临时文件，默认为 `true`
- `max_pages_per_batch` (查询参数): PDF分页处理时每批处理的最大页数，默认为 `5`，范围 1-20

#### 2.3 提取纯文本

**接口地址**: `POST /api/v1/document/extract/text`

**描述**: 从文档中提取纯文本内容

**请求参数**:
- `file` (文件): 要提取文本的文档文件 (必需)
- `max_length` (查询参数): 最大文本长度，超出部分将被截断 (可选)

#### 2.4 提取结构化数据

**接口地址**: `POST /api/v1/document/extract/structured`

**描述**: 从文档中提取结构化数据，可以指定要提取的元素类型

**请求参数**:
- `file` (文件): 要提取结构化数据的文档文件 (必需)
- `target_types` (查询参数): 目标元素类型，多个类型用逗号分隔，如: `Title,Table,List` (可选)

### 3. 工具接口

#### 3.1 获取支持的文件格式

**接口地址**: `GET /api/v1/document/formats`

**描述**: 获取支持的文件格式信息

#### 3.2 验证文件格式

**接口地址**: `GET /api/v1/document/validate/{filename}`

**描述**: 验证指定文件名的格式是否支持

#### 3.3 服务健康检查

**接口地址**: `GET /api/v1/document/health`

**描述**: 检查文档解析服务的健康状态

## 修正总结

本次检查发现并修正了以下问题：

1. **API路径前缀不一致**：将 `/api/documents` 修正为 `/api/v1/document`
2. **缺少cleanup参数**：在解析接口中添加了 `cleanup` 参数
3. **URL拼写错误**：修正了文档中的URL拼写错误
4. **参数文档完善**：添加了 `max_pages_per_batch` 参数的详细说明

现在API文档与实际实现完全一致，所有URL和参数都能正确对应。

---

**文档版本**: 1.1.0 (修正版)  
**最后更新**: 2024-01-01
**修正日期**: 2024-01-01