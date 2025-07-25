#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档解析模块

这个模块提供了完整的文档解析功能，支持PDF、Word、TXT等格式的文件解析，
并将解析结果转换为JSON格式。

主要组件：
- DocumentParser: 核心解析器类
- DocumentService: 文档解析服务类
- API: RESTful API接口

使用示例：
    from src.parser import DocumentParser, get_document_service
    
    # 使用解析器
    parser = DocumentParser()
    result = parser.parse_to_json('document.pdf')
    
    # 使用服务
    service = get_document_service()
    result = service.parse_uploaded_file(file_content, 'document.pdf')
"""

from .document_parser import (
    DocumentParser,
    DocumentParseError,
    parse_document_to_json,
    extract_text_from_document
)

from .document_service import (
    DocumentService,
    get_document_service
)

from .api import router as document_api_router

__version__ = "1.0.0"
__author__ = "Document Parser Team"
__description__ = "文档解析模块，支持PDF、Word、TXT等格式的文件解析"

# 导出的公共接口
__all__ = [
    # 核心类
    'DocumentParser',
    'DocumentService',
    'DocumentParseError',
    
    # 便捷函数
    'parse_document_to_json',
    'extract_text_from_document',
    'get_document_service',
    
    # API路由
    'document_api_router',
    
    # 元信息
    '__version__',
    '__author__',
    '__description__'
]

# 模块级别的配置
DEFAULT_CONFIG = {
    'temp_dir': None,  # 使用系统默认临时目录
    'cleanup_temp_files': True,  # 自动清理临时文件
    'include_metadata': True,  # 默认包含元数据
    'max_file_size': 50 * 1024 * 1024,  # 最大文件大小 50MB
}

# 支持的文件格式
SUPPORTED_FORMATS = {
    '.pdf': 'PDF文档',
    '.docx': 'Word文档',
    '.doc': 'Word文档（旧版）',
    '.txt': '纯文本文件',
    '.md': 'Markdown文件'
}


def get_module_info():
    """获取模块信息
    
    Returns:
        dict: 模块信息字典
    """
    return {
        'name': 'document_parser',
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'supported_formats': SUPPORTED_FORMATS,
        'default_config': DEFAULT_CONFIG
    }


def create_parser(config=None):
    """创建文档解析器实例的工厂函数
    
    Args:
        config (dict, optional): 配置参数
        
    Returns:
        DocumentParser: 解析器实例
    """
    return DocumentParser()


def create_service(temp_dir=None):
    """创建文档服务实例的工厂函数
    
    Args:
        temp_dir (str, optional): 临时目录路径
        
    Returns:
        DocumentService: 服务实例
    """
    return DocumentService(temp_dir=temp_dir)