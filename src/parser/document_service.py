#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档解析服务模块
提供文档解析的高级业务逻辑接口
"""

import json
import os
import tempfile
from typing import Dict, List, Any, Optional, Union, BinaryIO
from pathlib import Path
import logging
from datetime import datetime
import hashlib

from .document_parser import DocumentParser, DocumentParseError
from config.parser_config import parser_config

# 配置日志
logger = logging.getLogger(__name__)


class DocumentService:
    """文档解析服务类"""
    
    def __init__(self, temp_dir: Optional[str] = None, max_pages_per_batch: Optional[int] = None):
        """初始化文档服务
        
        Args:
            temp_dir: 临时文件目录，默认使用系统临时目录
            max_pages_per_batch: PDF分页处理时每批处理的最大页数
        """
        # 从配置中获取参数
        if max_pages_per_batch is None:
            max_pages_per_batch = parser_config.get_max_pages_per_batch()
        
        self.parser = DocumentParser(max_pages_per_batch=max_pages_per_batch)
        
        # 临时文件目录配置
        if temp_dir is None:
            temp_dir = parser_config.TEMP_FILE_CONFIG.get('temp_dir')
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_temp_filename(self, original_filename: str) -> str:
        """生成临时文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            str: 临时文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(original_filename.encode()).hexdigest()[:8]
        return f"{timestamp}_{file_hash}_{original_filename}"
    
    def _save_uploaded_file(self, file_content: bytes, filename: str) -> Path:
        """保存上传的文件到临时目录
        
        Args:
            file_content: 文件内容
            filename: 文件名
            
        Returns:
            Path: 保存的文件路径
        """
        temp_filename = self._generate_temp_filename(filename)
        temp_file_path = self.temp_dir / temp_filename
        
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"文件已保存到临时目录: {temp_file_path}")
        return temp_file_path
    
    def parse_uploaded_file(self, file_content: bytes, filename: str,
                           include_metadata: bool = True,
                           cleanup: bool = True) -> Dict[str, Any]:
        """解析上传的文件
        
        Args:
            file_content: 文件内容（字节）
            filename: 文件名
            include_metadata: 是否包含元数据
            cleanup: 是否清理临时文件
            
        Returns:
            Dict[str, Any]: 解析结果
            
        Raises:
            DocumentParseError: 解析失败
        """
        temp_file_path = None
        
        try:
            # 保存临时文件
            temp_file_path = self._save_uploaded_file(file_content, filename)
            
            # 解析文档
            result = self.parser.parse_to_json(
                file_path=temp_file_path,
                include_metadata=include_metadata
            )
            
            # 更新文档信息中的原始文件名
            result['document_info']['original_filename'] = filename
            result['document_info']['temp_file_path'] = str(temp_file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"解析上传文件失败: {str(e)}")
            raise DocumentParseError(f"解析上传文件失败: {str(e)}")
        
        finally:
            # 清理临时文件
            if cleanup and temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                    logger.info(f"临时文件已清理: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {str(e)}")
    
    def parse_file_stream(self, file_stream: BinaryIO, filename: str,
                         include_metadata: bool = True,
                         cleanup: bool = True) -> Dict[str, Any]:
        """解析文件流
        
        Args:
            file_stream: 文件流
            filename: 文件名
            include_metadata: 是否包含元数据
            cleanup: 是否清理临时文件
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        file_content = file_stream.read()
        return self.parse_uploaded_file(file_content, filename, include_metadata, cleanup)
    
    def batch_parse_files(self, files: List[Dict[str, Union[bytes, str]]],
                         include_metadata: bool = True,
                         cleanup: bool = True) -> List[Dict[str, Any]]:
        """批量解析文件
        
        Args:
            files: 文件列表，每个元素包含 'content' 和 'filename'
            include_metadata: 是否包含元数据
            cleanup: 是否清理临时文件
            
        Returns:
            List[Dict[str, Any]]: 解析结果列表
        """
        results = []
        
        for file_info in files:
            try:
                result = self.parse_uploaded_file(
                    file_content=file_info['content'],
                    filename=file_info['filename'],
                    include_metadata=include_metadata,
                    cleanup=cleanup
                )
                results.append({
                    'success': True,
                    'filename': file_info['filename'],
                    'data': result
                })
            except Exception as e:
                logger.error(f"批量解析文件 {file_info['filename']} 失败: {str(e)}")
                results.append({
                    'success': False,
                    'filename': file_info['filename'],
                    'error': str(e)
                })
        
        return results
    
    def extract_structured_data(self, file_content: bytes, filename: str,
                               target_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """提取结构化数据
        
        Args:
            file_content: 文件内容
            filename: 文件名
            target_types: 目标元素类型列表，如 ['Title', 'Table', 'List']
            
        Returns:
            Dict[str, Any]: 结构化数据
        """
        # 如果未指定目标类型，使用配置中的默认值
        if target_types is None:
            target_types = parser_config.get_default_target_types()
        temp_file_path = None
        
        try:
            # 保存临时文件
            temp_file_path = self._save_uploaded_file(file_content, filename)
            
            if target_types:
                # 按类型提取
                elements = self.parser.extract_by_type(temp_file_path, target_types)
            else:
                # 提取所有元素
                parsed_result = self.parser.parse_to_json(temp_file_path)
                elements = parsed_result['content']
            
            # 按类型分组
            grouped_data = {}
            for element in elements:
                element_type = element['type']
                if element_type not in grouped_data:
                    grouped_data[element_type] = []
                grouped_data[element_type].append(element)
            
            return {
                'document_info': {
                    'filename': filename,
                    'extracted_at': datetime.now().isoformat(),
                    'total_elements': len(elements),
                    'element_types': list(grouped_data.keys())
                },
                'structured_data': grouped_data
            }
            
        finally:
            # 清理临时文件
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {str(e)}")
    
    def extract_text_summary(self, file_content: bytes, filename: str,
                           max_length: Optional[int] = None) -> Dict[str, Any]:
        """提取文本摘要
        
        Args:
            file_content: 文件内容
            filename: 文件名
            max_length: 最大文本长度
            
        Returns:
            Dict[str, Any]: 文本摘要
        """
        # 如果未指定最大长度，使用配置中的默认值
        if max_length is None:
            max_length = parser_config.TEXT_EXTRACTION_CONFIG['max_text_length']
        temp_file_path = None
        
        try:
            # 保存临时文件
            temp_file_path = self._save_uploaded_file(file_content, filename)
            
            # 提取纯文本
            full_text = self.parser.extract_text_only(temp_file_path)
            
            # 截断文本（如果指定了最大长度）
            if max_length and len(full_text) > max_length:
                truncated_text = full_text[:max_length] + "..."
                is_truncated = True
            else:
                truncated_text = full_text
                is_truncated = False
            
            return {
                'document_info': {
                    'filename': filename,
                    'extracted_at': datetime.now().isoformat(),
                    'full_text_length': len(full_text),
                    'is_truncated': is_truncated
                },
                'text_content': truncated_text
            }
            
        finally:
            # 清理临时文件
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {str(e)}")
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """获取支持的文件格式
        
        Returns:
            Dict[str, List[str]]: 支持的文件格式信息
        """
        return {
            'supported_extensions': list(self.parser.SUPPORTED_EXTENSIONS.keys()),
            'supported_types': list(set(self.parser.SUPPORTED_EXTENSIONS.values())),
            'format_mapping': self.parser.SUPPORTED_EXTENSIONS
        }
    
    def is_supported_file(self, filename: str) -> bool:
        """检查文件是否支持解析
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否支持解析
        """
        return self.parser.is_supported_file(filename)
    
    def validate_file(self, filename: str) -> Dict[str, Any]:
        """验证文件是否支持解析
        
        Args:
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        is_supported = extension in self.parser.SUPPORTED_EXTENSIONS
        file_type = self.parser.SUPPORTED_EXTENSIONS.get(extension) if is_supported else None
        
        return {
            'filename': filename,
            'extension': extension,
            'is_supported': is_supported,
            'file_type': file_type,
            'supported_formats': self.get_supported_formats()
        }


# 全局服务实例
_document_service = None


def get_document_service(max_pages_per_batch: Optional[int] = None) -> DocumentService:
    """获取文档服务实例（单例模式）
    
    Args:
        max_pages_per_batch: PDF分页处理时每批处理的最大页数
        
    Returns:
        DocumentService: 文档服务实例
    """
    global _document_service
    if _document_service is None:
        _document_service = DocumentService(max_pages_per_batch=max_pages_per_batch)
    return _document_service