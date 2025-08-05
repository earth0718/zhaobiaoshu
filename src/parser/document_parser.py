#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档解析器模块
使用unstructured库解析PDF、Word、TXT等文件并转换为JSON格式
"""

import json
import os
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from datetime import datetime
import PyPDF2
from io import BytesIO

from unstructured.partition.auto import partition
# 暂时注释PDF导入以避免依赖问题
# from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text
from unstructured.documents.elements import Element

# 导入配置
from config.parser_config import parser_config

# 配置日志
logger = logging.getLogger(__name__)


class DocumentParseError(Exception):
    """文档解析异常"""
    pass


class DocumentParser:
    """文档解析器类"""
    
    def __init__(self, max_pages_per_batch: Optional[int] = None):
        """初始化文档解析器
        
        Args:
            max_pages_per_batch: 每批处理的最大页数，用于控制内存使用
        """
        # 从配置中获取参数
        self.max_pages_per_batch = (
            max_pages_per_batch if max_pages_per_batch is not None 
            else parser_config.get_max_pages_per_batch()
        )
        
        # 支持的文件类型从配置中获取
        self.SUPPORTED_EXTENSIONS = parser_config.get_supported_extensions()
        
        # 解析器配置从配置中获取
        self.parser_config = parser_config.PARSER_STRATEGIES
    
    def is_supported_file(self, file_path: Union[str, Path]) -> bool:
        """检查文件是否支持解析
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持解析
        """
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def get_file_type(self, file_path: Union[str, Path]) -> str:
        """获取文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件类型
            
        Raises:
            DocumentParseError: 不支持的文件类型
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise DocumentParseError(f"不支持的文件类型: {extension}")
        
        return self.SUPPORTED_EXTENSIONS[extension]
    
    def parse_document(self, file_path: Union[str, Path]) -> List[Element]:
        """解析文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Element]: 解析后的元素列表
            
        Raises:
            DocumentParseError: 解析失败
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DocumentParseError(f"文件不存在: {file_path}")
        
        if not self.is_supported_file(file_path):
            raise DocumentParseError(f"不支持的文件类型: {file_path.suffix}")
        
        file_type = self.get_file_type(file_path)
        config = self.parser_config.get(file_type, {})
        
        try:
            logger.info(f"开始解析文档: {file_path}")
            
            # 根据文件类型选择解析方法
            if file_type == 'pdf':
                # 使用分页处理PDF
                elements = self._parse_pdf_by_pages(file_path)
            elif file_type == 'docx':
                elements = partition_docx(
                    filename=str(file_path),
                    **config
                )
            elif file_type == 'text':
                elements = partition_text(
                    filename=str(file_path),
                    **config
                )
            elif file_type == 'image':
                # 添加图片处理
                from unstructured.partition.image import partition_image
                elements = partition_image(
                    filename=str(file_path),
                    strategy="hi_res",  # 使用高精度OCR
                    **config
                )
            else:
                # 使用自动检测
                elements = partition(
                    filename=str(file_path)
                )
            
            logger.info(f"文档解析完成，共提取 {len(elements)} 个元素")
            return elements
            
        except Exception as e:
            logger.error(f"文档解析失败: {str(e)}")
            raise DocumentParseError(f"文档解析失败: {str(e)}")
    
    def elements_to_dict(self, elements: List[Element]) -> List[Dict[str, Any]]:
        """将元素列表转换为字典列表
        
        Args:
            elements: 元素列表
            
        Returns:
            List[Dict[str, Any]]: 字典列表
        """
        result = []
        
        for element in elements:
            element_dict = {
                'type': element.category,
                'text': str(element),
                'metadata': {}
            }
            
            # 添加元数据
            if hasattr(element, 'metadata') and element.metadata:
                metadata = element.metadata.to_dict() if hasattr(element.metadata, 'to_dict') else element.metadata
                element_dict['metadata'] = metadata
            
            # 添加其他属性
            if hasattr(element, 'id'):
                element_dict['id'] = element.id
            
            result.append(element_dict)
        
        return result
    
    def parse_to_json(self, file_path: Union[str, Path], 
                     output_file: Optional[Union[str, Path]] = None,
                     include_metadata: bool = True) -> Dict[str, Any]:
        """解析文档并转换为JSON格式
        
        Args:
            file_path: 输入文件路径
            output_file: 输出JSON文件路径（可选）
            include_metadata: 是否包含元数据
            
        Returns:
            Dict[str, Any]: JSON格式的解析结果
            
        Raises:
            DocumentParseError: 解析失败
        """
        file_path = Path(file_path)
        
        # 解析文档
        elements = self.parse_document(file_path)
        
        # 转换为字典
        elements_dict = self.elements_to_dict(elements)
        
        # 构建最终结果
        result = {
            'document_info': {
                'filename': file_path.name,
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'file_type': self.get_file_type(file_path),
                'parsed_at': datetime.now().isoformat(),
                'total_elements': len(elements)
            },
            'content': elements_dict
        }
        
        # 如果不包含元数据，移除metadata字段
        if not include_metadata:
            for item in result['content']:
                item.pop('metadata', None)
        
        # 保存到文件
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"解析结果已保存到: {output_path}")
        
        return result
    
    def extract_text_only(self, file_path: Union[str, Path]) -> str:
        """仅提取文档中的纯文本
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 提取的纯文本
        """
        elements = self.parse_document(file_path)
        return '\n'.join([str(element) for element in elements])
    
    def extract_by_type(self, file_path: Union[str, Path], 
                       element_types: List[str]) -> List[Dict[str, Any]]:
        """按类型提取文档元素
        
        Args:
            file_path: 文件路径
            element_types: 要提取的元素类型列表
            
        Returns:
            List[Dict[str, Any]]: 指定类型的元素列表
        """
        elements = self.parse_document(file_path)
        filtered_elements = [elem for elem in elements if elem.category in element_types]
        return self.elements_to_dict(filtered_elements)
    
    def _get_pdf_page_count(self, file_path: Path) -> int:
        """获取PDF文件的页数
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            int: 页数
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            logger.warning(f"无法获取PDF页数，使用默认方法: {str(e)}")
            return -1
    
    def _extract_pdf_pages(self, file_path: Path, start_page: int, end_page: int) -> bytes:
        """提取PDF指定页面范围
        
        Args:
            file_path: PDF文件路径
            start_page: 起始页（从0开始）
            end_page: 结束页（不包含）
            
        Returns:
            bytes: 提取的PDF页面数据
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_writer = PyPDF2.PdfWriter()
                
                # 添加指定范围的页面
                for page_num in range(start_page, min(end_page, len(pdf_reader.pages))):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                # 将PDF写入内存
                output_buffer = BytesIO()
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)
                
                return output_buffer.getvalue()
        except Exception as e:
            logger.error(f"提取PDF页面失败: {str(e)}")
            raise DocumentParseError(f"提取PDF页面失败: {str(e)}")
    
    def _parse_pdf_by_pages(self, file_path: Path) -> List[Element]:
        """按页处理PDF文件
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            List[Element]: 解析后的元素列表
        """
        logger.info(f"开始按页处理PDF: {file_path}")
        
        # 获取总页数
        total_pages = self._get_pdf_page_count(file_path)
        
        if total_pages <= 0:
            # 如果无法获取页数，使用原始方法
            logger.info("无法获取PDF页数，使用原始解析方法")
            return partition(filename=str(file_path))
        
        logger.info(f"PDF总页数: {total_pages}")
        
        all_elements = []
        
        # 按批次处理页面
        for start_page in range(0, total_pages, self.max_pages_per_batch):
            end_page = min(start_page + self.max_pages_per_batch, total_pages)
            
            logger.info(f"处理页面 {start_page + 1}-{end_page} / {total_pages}")
            
            try:
                # 提取当前批次的页面
                page_data = self._extract_pdf_pages(file_path, start_page, end_page)
                
                # 创建临时文件
                temp_file = BytesIO(page_data)
                
                # 解析当前批次的页面
                batch_elements = partition(
                    file=temp_file,
                    content_type="application/pdf",
                    include_page_breaks=True
                )
                
                # 为每个元素添加页面信息
                for element in batch_elements:
                    if hasattr(element, 'metadata'):
                        if not hasattr(element.metadata, 'page_number'):
                            # 估算页面号（这是一个近似值）
                            element.metadata.page_number = start_page + 1
                        # 调整页面号到全局范围
                        if hasattr(element.metadata, 'page_number') and element.metadata.page_number:
                            element.metadata.page_number += start_page
                
                all_elements.extend(batch_elements)
                
                logger.info(f"批次 {start_page + 1}-{end_page} 处理完成，提取 {len(batch_elements)} 个元素")
                
            except Exception as e:
                logger.error(f"处理页面 {start_page + 1}-{end_page} 时出错: {str(e)}")
                # 继续处理下一批次，不中断整个过程
                continue
        
        logger.info(f"PDF分页处理完成，总共提取 {len(all_elements)} 个元素")
        return all_elements


# 便捷函数
def parse_document_to_json(file_path: Union[str, Path], 
                          output_file: Optional[Union[str, Path]] = None,
                          include_metadata: bool = True) -> Dict[str, Any]:
    """解析文档为JSON格式的便捷函数
    
    Args:
        file_path: 输入文件路径
        output_file: 输出JSON文件路径（可选）
        include_metadata: 是否包含元数据
        
    Returns:
        Dict[str, Any]: JSON格式的解析结果
    """
    parser = DocumentParser()
    return parser.parse_to_json(file_path, output_file, include_metadata)


def extract_text_from_document(file_path: Union[str, Path]) -> str:
    """从文档中提取纯文本的便捷函数
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 提取的纯文本
    """
    parser = DocumentParser()
    return parser.extract_text_only(file_path)