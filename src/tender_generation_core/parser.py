#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档解析模块

功能说明：
- 支持多种文档格式的文本提取，包括DOCX和PDF格式
- 使用python-docx库处理Word文档，使用PyMuPDF处理PDF文档
- 提供统一的文档解析接口，根据文件扩展名自动选择合适的解析器
- 包含错误处理机制，确保文档解析的稳定性
"""

import docx
import fitz  # PyMuPDF

def get_text_from_docx(filepath):
    """从 .docx 文件中提取文本"""
    try:
        doc = docx.Document(filepath)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading docx file {filepath}: {e}")
        return None

def get_text_from_pdf(filepath):
    """从 .pdf 文件中提取文本"""
    try:
        doc = fitz.open(filepath)
        full_text = []
        for page in doc:
            full_text.append(page.get_text())
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading pdf file {filepath}: {e}")
        return None

def parse_document_text(filepath):
    """根据文件扩展名选择合适的解析器"""
    # 检查文件路径是否包含扩展名
    if '.' not in filepath:
        raise ValueError(f"文件路径没有扩展名: {filepath}")
    
    # 安全地分割文件路径和扩展名
    parts = filepath.rsplit('.', 1)
    if len(parts) != 2:
        raise ValueError(f"无法解析文件扩展名: {filepath}")
    
    _, extension = parts
    extension = extension.lower()

    if extension == 'docx':
        return get_text_from_docx(filepath)
    elif extension == 'pdf':
        return get_text_from_pdf(filepath)
    else:
        raise ValueError(f"不支持的文件类型: {extension}")