#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多文件处理配置管理模块

功能说明：
- 管理多文件处理相关的配置参数
- 提供配置文件读取和验证功能
- 支持配置参数的动态更新
- 提供默认配置和配置验证
"""

import os
import configparser
from typing import Dict, Any, List, Optional
from pathlib import Path


class MultiFileConfig:
    """多文件处理配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        self.config = configparser.ConfigParser()
        
        # 设置默认配置文件路径
        if config_file is None:
            config_dir = Path(__file__).parent
            config_file = config_dir / "multi_file_config.ini"
        
        self.config_file = str(config_file)
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file, encoding='utf-8')
                print(f"已加载多文件处理配置: {self.config_file}")
            else:
                print(f"配置文件不存在，使用默认配置: {self.config_file}")
                self._create_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        # 多文件处理配置
        self.config.add_section('multi_file_processing')
        self.config.set('multi_file_processing', 'max_files', '10')
        self.config.set('multi_file_processing', 'max_file_size_mb', '50')
        self.config.set('multi_file_processing', 'supported_formats', 'pdf,docx')
        self.config.set('multi_file_processing', 'enable_content_optimization', 'true')
        self.config.set('multi_file_processing', 'enable_duplicate_removal', 'true')
        self.config.set('multi_file_processing', 'enable_similar_section_detection', 'true')
        self.config.set('multi_file_processing', 'similarity_threshold', '0.7')
        self.config.set('multi_file_processing', 'enable_cache', 'true')
        self.config.set('multi_file_processing', 'cache_max_size', '50')
        self.config.set('multi_file_processing', 'max_concurrent_chunks', '10')
        self.config.set('multi_file_processing', 'chunk_processing_timeout', '300')
        
        # 输出设置
        self.config.add_section('output_settings')
        self.config.set('output_settings', 'default_project_name', '招标项目')
        self.config.set('output_settings', 'markdown_output_dir', 'download/markdown')
        self.config.set('output_settings', 'word_output_dir', 'download/word')
        self.config.set('output_settings', 'filename_template', 'tender_{timestamp}_{task_id}')
        self.config.set('output_settings', 'include_source_info', 'true')
        self.config.set('output_settings', 'default_sections', 
                       '第一章 采购公告,第二章 供应商须知,第三章 评审办法,第四章 合同条款及格式,第五章 采购人要求,第六章 响应文件格式')
        
        # 质量控制设置
        self.config.add_section('quality_settings')
        self.config.set('quality_settings', 'min_content_length', '100')
        self.config.set('quality_settings', 'max_merged_content_length', '1000000')
        self.config.set('quality_settings', 'max_chunk_size', '4000')
        self.config.set('quality_settings', 'chunk_overlap', '200')
        
        # 错误处理设置
        self.config.add_section('error_handling')
        self.config.set('error_handling', 'continue_on_parse_error', 'true')
        self.config.set('error_handling', 'max_retry_attempts', '3')
        self.config.set('error_handling', 'retry_interval', '5')
        self.config.set('error_handling', 'save_error_logs', 'true')
        
        # 日志设置
        self.config.add_section('logging')
        self.config.set('logging', 'log_level', 'INFO')
        self.config.set('logging', 'enable_verbose_logging', 'false')
        self.config.set('logging', 'log_file_path', 'logs/multi_file_processing.log')
    
    def get_max_files(self) -> int:
        """获取最大文件数量限制"""
        return self.config.getint('multi_file_processing', 'max_files', fallback=10)
    
    def get_max_file_size_mb(self) -> int:
        """获取单个文件最大大小（MB）"""
        return self.config.getint('multi_file_processing', 'max_file_size_mb', fallback=50)
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式列表"""
        formats_str = self.config.get('multi_file_processing', 'supported_formats', fallback='pdf,docx')
        return [fmt.strip().lower() for fmt in formats_str.split(',')]
    
    def is_content_optimization_enabled(self) -> bool:
        """是否启用内容优化"""
        return self.config.getboolean('multi_file_processing', 'enable_content_optimization', fallback=True)
    
    def is_duplicate_removal_enabled(self) -> bool:
        """是否启用重复内容移除"""
        return self.config.getboolean('multi_file_processing', 'enable_duplicate_removal', fallback=True)
    
    def is_similar_section_detection_enabled(self) -> bool:
        """是否启用相似章节检测"""
        return self.config.getboolean('multi_file_processing', 'enable_similar_section_detection', fallback=True)
    
    def get_similarity_threshold(self) -> float:
        """获取相似度阈值"""
        return self.config.getfloat('multi_file_processing', 'similarity_threshold', fallback=0.7)
    
    def is_cache_enabled(self) -> bool:
        """是否启用缓存"""
        return self.config.getboolean('multi_file_processing', 'enable_cache', fallback=True)
    
    def get_cache_max_size(self) -> int:
        """获取缓存最大大小"""
        return self.config.getint('multi_file_processing', 'cache_max_size', fallback=50)
    
    def get_max_concurrent_chunks(self) -> int:
        """获取最大并发处理块数"""
        return self.config.getint('multi_file_processing', 'max_concurrent_chunks', fallback=10)
    
    def get_chunk_processing_timeout(self) -> int:
        """获取块处理超时时间（秒）"""
        return self.config.getint('multi_file_processing', 'chunk_processing_timeout', fallback=300)
    
    def get_default_project_name(self) -> str:
        """获取默认项目名称"""
        return self.config.get('output_settings', 'default_project_name', fallback='招标项目')
    
    def get_markdown_output_dir(self) -> str:
        """获取Markdown输出目录"""
        return self.config.get('output_settings', 'markdown_output_dir', fallback='download/markdown')
    
    def get_word_output_dir(self) -> str:
        """获取Word输出目录"""
        return self.config.get('output_settings', 'word_output_dir', fallback='download/word')
    
    def get_filename_template(self) -> str:
        """获取文件名模板"""
        return self.config.get('output_settings', 'filename_template', fallback='tender_{timestamp}_{task_id}')
    
    def is_source_info_included(self) -> bool:
        """是否包含源文件信息"""
        return self.config.getboolean('output_settings', 'include_source_info', fallback=True)
    
    def get_default_sections(self) -> List[str]:
        """获取默认章节列表"""
        sections_str = self.config.get('output_settings', 'default_sections', 
                                     fallback='第一章 采购公告,第二章 供应商须知,第三章 评审办法,第四章 合同条款及格式,第五章 采购人要求,第六章 响应文件格式')
        return [section.strip() for section in sections_str.split(',')]
    
    def get_min_content_length(self) -> int:
        """获取最小内容长度"""
        return self.config.getint('quality_settings', 'min_content_length', fallback=100)
    
    def get_max_merged_content_length(self) -> int:
        """获取最大合并内容长度"""
        return self.config.getint('quality_settings', 'max_merged_content_length', fallback=1000000)
    
    def get_max_chunk_size(self) -> int:
        """获取最大文本块大小"""
        return self.config.getint('quality_settings', 'max_chunk_size', fallback=4000)
    
    def get_chunk_overlap(self) -> int:
        """获取文本块重叠大小"""
        return self.config.getint('quality_settings', 'chunk_overlap', fallback=200)
    
    def should_continue_on_parse_error(self) -> bool:
        """是否在解析错误时继续处理"""
        return self.config.getboolean('error_handling', 'continue_on_parse_error', fallback=True)
    
    def get_max_retry_attempts(self) -> int:
        """获取最大重试次数"""
        return self.config.getint('error_handling', 'max_retry_attempts', fallback=3)
    
    def get_retry_interval(self) -> int:
        """获取重试间隔（秒）"""
        return self.config.getint('error_handling', 'retry_interval', fallback=5)
    
    def should_save_error_logs(self) -> bool:
        """是否保存错误日志"""
        return self.config.getboolean('error_handling', 'save_error_logs', fallback=True)
    
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.config.get('logging', 'log_level', fallback='INFO')
    
    def is_verbose_logging_enabled(self) -> bool:
        """是否启用详细日志"""
        return self.config.getboolean('logging', 'enable_verbose_logging', fallback=False)
    
    def get_log_file_path(self) -> str:
        """获取日志文件路径"""
        return self.config.get('logging', 'log_file_path', fallback='logs/multi_file_processing.log')
    
    def validate_file_format(self, filename: str) -> bool:
        """验证文件格式是否支持
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否支持该格式
        """
        if not filename:
            return False
        
        file_extension = os.path.splitext(filename)[1].lower().lstrip('.')
        supported_formats = self.get_supported_formats()
        return file_extension in supported_formats
    
    def validate_file_count(self, file_count: int) -> bool:
        """验证文件数量是否在限制范围内
        
        Args:
            file_count: 文件数量
            
        Returns:
            bool: 是否在限制范围内
        """
        max_files = self.get_max_files()
        return 1 <= file_count <= max_files
    
    def get_config_dict(self) -> Dict[str, Any]:
        """获取所有配置的字典表示
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        config_dict = {}
        for section_name in self.config.sections():
            config_dict[section_name] = dict(self.config.items(section_name))
        return config_dict
    
    def update_config(self, section: str, key: str, value: str):
        """更新配置项
        
        Args:
            section: 配置节名
            key: 配置键
            value: 配置值
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, value)
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 确保配置文件目录存在
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")


# 全局配置实例
multi_file_config = MultiFileConfig()