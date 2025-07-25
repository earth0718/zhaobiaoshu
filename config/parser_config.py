#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档解析器配置模块
包含影响解析结果的重要参数配置
"""

from typing import Dict, List, Any


class ParserConfig:
    """文档解析器配置类"""
    
    # 支持的文件类型映射
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'pdf',
        '.docx': 'docx', 
        '.doc': 'docx',
        '.txt': 'text',
        '.md': 'text'
    }
    
    # PDF分页处理配置
    PDF_BATCH_CONFIG = {
        'max_pages_per_batch': 5,  # 每批处理的最大页数，影响内存使用和处理速度
        'enable_batch_processing': True,  # 是否启用分页处理
    }
    
    # 解析器策略配置
    PARSER_STRATEGIES = {
        'pdf': {
            'strategy': 'auto',  # 可选: auto, fast, ocr_only, hi_res
            'include_page_breaks': True,  # 是否包含分页符
            'infer_table_structure': True,  # 是否推断表格结构
            'extract_images': False,  # 是否提取图片（影响性能）
        },
        'docx': {
            'include_page_breaks': True,
            'infer_table_structure': True,
            'extract_images': False,
        },
        'text': {
            'include_page_breaks': False,
            'encoding': 'utf-8',  # 文本文件编码
        }
    }
    
    # 文本提取配置
    TEXT_EXTRACTION_CONFIG = {
        'max_text_length': 1000000,  # 最大文本长度（字符数）
        'enable_text_cleaning': True,  # 是否启用文本清理
        'remove_extra_whitespace': True,  # 是否移除多余空白字符
    }
    
    # 结构化数据提取配置
    STRUCTURED_DATA_CONFIG = {
        'default_target_types': ['Title', 'Header', 'Table', 'List', 'Text'],  # 默认提取的元素类型
        'group_by_type': True,  # 是否按类型分组
        'include_element_metadata': True,  # 是否包含元素元数据
    }
    
    # 临时文件配置
    TEMP_FILE_CONFIG = {
        'auto_cleanup': True,  # 是否自动清理临时文件
        'temp_dir': None,  # 临时文件目录，None表示使用系统默认
        'filename_hash_length': 8,  # 文件名哈希长度
    }
    
    # 批量处理配置
    BATCH_PROCESSING_CONFIG = {
        'max_concurrent_files': 5,  # 最大并发处理文件数
        'continue_on_error': True,  # 遇到错误时是否继续处理其他文件
        'include_error_details': True,  # 是否包含详细错误信息
    }
    
    # 性能优化配置
    PERFORMANCE_CONFIG = {
        'enable_caching': False,  # 是否启用缓存（暂未实现）
        'memory_limit_mb': 512,  # 内存限制（MB）
        'timeout_seconds': 300,  # 处理超时时间（秒）
    }
    
    @classmethod
    def get_parser_config(cls, file_type: str) -> Dict[str, Any]:
        """获取指定文件类型的解析配置
        
        Args:
            file_type: 文件类型 ('pdf', 'docx', 'text')
            
        Returns:
            Dict[str, Any]: 解析配置
        """
        return cls.PARSER_STRATEGIES.get(file_type, {})
    
    @classmethod
    def get_max_pages_per_batch(cls) -> int:
        """获取PDF分页处理的最大页数
        
        Returns:
            int: 最大页数
        """
        return cls.PDF_BATCH_CONFIG['max_pages_per_batch']
    
    @classmethod
    def is_batch_processing_enabled(cls) -> bool:
        """检查是否启用分页处理
        
        Returns:
            bool: 是否启用
        """
        return cls.PDF_BATCH_CONFIG['enable_batch_processing']
    
    @classmethod
    def get_supported_extensions(cls) -> Dict[str, str]:
        """获取支持的文件扩展名映射
        
        Returns:
            Dict[str, str]: 扩展名到类型的映射
        """
        return cls.SUPPORTED_EXTENSIONS.copy()
    
    @classmethod
    def get_default_target_types(cls) -> List[str]:
        """获取默认的目标元素类型
        
        Returns:
            List[str]: 元素类型列表
        """
        return cls.STRUCTURED_DATA_CONFIG['default_target_types'].copy()


# 全局配置实例
parser_config = ParserConfig()