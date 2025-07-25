#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文本分块模块

功能说明：
- 使用LangChain的RecursiveCharacterTextSplitter实现高级文本分块
- 支持智能分隔符选择，优先在段落、句子等自然边界处分割
- 提供配置化参数管理，支持自定义分块大小和重叠度
- 包含回退机制，确保分块操作的稳定性
"""

import os
import configparser
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 加载配置文件
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'tender_generation_config.ini')

try:
    config.read(config_path, encoding='utf-8')
except Exception as e:
    print(f"读取配置文件失败: {e}，将使用默认配置")

# 从配置文件读取参数，如果读取失败则使用默认值
DEFAULT_CHUNK_SIZE = 2000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_SEPARATORS = ["\n\n", "\n", "。", "！", "？", ".", " ", ""]

def get_chunking_config():
    """
    从配置文件获取文本分块参数
    
    :return: tuple (chunk_size, chunk_overlap, separators)
    """
    try:
        chunk_size = config.getint('TextChunking', 'ChunkSize', fallback=DEFAULT_CHUNK_SIZE)
        chunk_overlap = config.getint('TextChunking', 'ChunkOverlap', fallback=DEFAULT_CHUNK_OVERLAP)
        
        # 解析分隔符配置
        separators_str = config.get('TextChunking', 'Separators', fallback='')
        if separators_str:
            # 处理转义字符
            separators = [sep.replace('\\n', '\n') for sep in separators_str.split(',')]
            # 添加默认的空格和空字符串分隔符
            separators.extend([" ", ""])
        else:
            separators = DEFAULT_SEPARATORS
            
        return chunk_size, chunk_overlap, separators
    except Exception as e:
        print(f"读取分块配置失败: {e}，使用默认配置")
        return DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, DEFAULT_SEPARATORS

def chunk_text(text, chunk_size=None, chunk_overlap=None, separators=None):
    """
    使用 LangChain 的 RecursiveCharacterTextSplitter 将文本分割成指定大小的块。
    
    该函数支持智能分隔符选择，优先在段落、句子等自然边界处分割文本，
    提供比简单字符分割更好的语义完整性。

    :param text: 要分割的原始文本
    :param chunk_size: 每个块的目标大小（字符数），如果为None则从配置文件读取
    :param chunk_overlap: 块之间的重叠大小（字符数），如果为None则从配置文件读取
    :param separators: 分隔符列表，如果为None则从配置文件读取
    :return: 文本块列表
    """
    if not isinstance(text, str):
        return []
    
    if not text.strip():
        return []
    
    # 如果参数为None，从配置文件获取
    if chunk_size is None or chunk_overlap is None or separators is None:
        config_chunk_size, config_chunk_overlap, config_separators = get_chunking_config()
        chunk_size = chunk_size or config_chunk_size
        chunk_overlap = chunk_overlap or config_chunk_overlap
        separators = separators or config_separators
    
    try:
        # 创建 RecursiveCharacterTextSplitter 实例
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False,
        )
        
        # 执行文本分割
        chunks = text_splitter.split_text(text)
        return chunks
        
    except Exception as e:
        print(f"使用 LangChain 分块失败: {e}，回退到简单分块方法")
        # 回退到简单的分块方法
        return _fallback_chunk_text(text, chunk_size, chunk_overlap)

def _fallback_chunk_text(text, chunk_size, chunk_overlap):
    """
    简单的回退分块方法，当 LangChain 分块失败时使用
    
    :param text: 要分割的原始文本
    :param chunk_size: 每个块的目标大小（字符数）
    :param chunk_overlap: 块之间的重叠大小（字符数）
    :return: 文本块列表
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
        if start >= len(text):
            break
    return chunks