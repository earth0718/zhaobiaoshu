#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理API模块
提供配置查看和修改的接口
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from config.parser_config import parser_config 
# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
config_router = APIRouter(tags=["配置管理"])


class ConfigUpdateRequest(BaseModel):
    """配置更新请求模型"""
    max_pages_per_batch: Optional[int] = None
    pdf_strategy: Optional[str] = None
    include_page_breaks: Optional[bool] = None
    infer_table_structure: Optional[bool] = None
    max_text_length: Optional[int] = None
    auto_cleanup: Optional[bool] = None


@config_router.get("/parser", summary="获取解析器配置")
async def get_parser_config() -> Dict[str, Any]:
    """获取当前的解析器配置
    
    Returns:
        Dict[str, Any]: 当前配置信息
    """
    try:
        return {
            "pdf_batch_config": parser_config.PDF_BATCH_CONFIG,
            "parser_strategies": parser_config.PARSER_STRATEGIES,
            "text_extraction_config": parser_config.TEXT_EXTRACTION_CONFIG,
            "structured_data_config": parser_config.STRUCTURED_DATA_CONFIG,
            "temp_file_config": parser_config.TEMP_FILE_CONFIG,
            "batch_processing_config": parser_config.BATCH_PROCESSING_CONFIG,
            "performance_config": parser_config.PERFORMANCE_CONFIG,
            "supported_extensions": parser_config.SUPPORTED_EXTENSIONS
        }
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@config_router.get("/parser/pdf", summary="获取PDF解析配置")
async def get_pdf_config() -> Dict[str, Any]:
    """获取PDF解析的详细配置
    
    Returns:
        Dict[str, Any]: PDF解析配置
    """
    try:
        return {
            "batch_config": parser_config.PDF_BATCH_CONFIG,
            "parser_strategy": parser_config.get_parser_config('pdf'),
            "max_pages_per_batch": parser_config.get_max_pages_per_batch(),
            "batch_processing_enabled": parser_config.is_batch_processing_enabled()
        }
    except Exception as e:
        logger.error(f"获取PDF配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取PDF配置失败: {str(e)}")


@config_router.get("/parser/supported-formats", summary="获取支持的文件格式")
async def get_supported_formats() -> Dict[str, Any]:
    """获取支持的文件格式信息
    
    Returns:
        Dict[str, Any]: 支持的文件格式
    """
    try:
        extensions = parser_config.get_supported_extensions()
        return {
            "supported_extensions": list(extensions.keys()),
            "supported_types": list(set(extensions.values())),
            "format_mapping": extensions,
            "total_formats": len(extensions)
        }
    except Exception as e:
        logger.error(f"获取支持格式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取支持格式失败: {str(e)}")


@config_router.get("/parser/text-extraction", summary="获取文本提取配置")
async def get_text_extraction_config() -> Dict[str, Any]:
    """获取文本提取配置
    
    Returns:
        Dict[str, Any]: 文本提取配置
    """
    try:
        return {
            "text_extraction_config": parser_config.TEXT_EXTRACTION_CONFIG,
            "default_target_types": parser_config.get_default_target_types()
        }
    except Exception as e:
        logger.error(f"获取文本提取配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文本提取配置失败: {str(e)}")


@config_router.put("/parser/update", summary="更新解析器配置")
async def update_parser_config(config_update: ConfigUpdateRequest) -> Dict[str, Any]:
    """更新解析器配置
    
    Args:
        config_update: 配置更新请求
        
    Returns:
        Dict[str, Any]: 更新结果
    """
    try:
        updated_fields = []
        
        # 更新PDF批处理配置
        if config_update.max_pages_per_batch is not None:
            if config_update.max_pages_per_batch > 0:
                parser_config.PDF_BATCH_CONFIG['max_pages_per_batch'] = config_update.max_pages_per_batch
                updated_fields.append('max_pages_per_batch')
            else:
                raise HTTPException(status_code=400, detail="max_pages_per_batch必须大于0")
        
        # 更新PDF策略配置
        if config_update.pdf_strategy is not None:
            valid_strategies = ['auto', 'fast', 'ocr_only', 'hi_res']
            if config_update.pdf_strategy in valid_strategies:
                parser_config.PARSER_STRATEGIES['pdf']['strategy'] = config_update.pdf_strategy
                updated_fields.append('pdf_strategy')
            else:
                raise HTTPException(status_code=400, detail=f"pdf_strategy必须是以下值之一: {valid_strategies}")
        
        # 更新分页符配置
        if config_update.include_page_breaks is not None:
            parser_config.PARSER_STRATEGIES['pdf']['include_page_breaks'] = config_update.include_page_breaks
            parser_config.PARSER_STRATEGIES['docx']['include_page_breaks'] = config_update.include_page_breaks
            updated_fields.append('include_page_breaks')
        
        # 更新表格结构推断配置
        if config_update.infer_table_structure is not None:
            parser_config.PARSER_STRATEGIES['pdf']['infer_table_structure'] = config_update.infer_table_structure
            parser_config.PARSER_STRATEGIES['docx']['infer_table_structure'] = config_update.infer_table_structure
            updated_fields.append('infer_table_structure')
        
        # 更新最大文本长度
        if config_update.max_text_length is not None:
            if config_update.max_text_length > 0:
                parser_config.TEXT_EXTRACTION_CONFIG['max_text_length'] = config_update.max_text_length
                updated_fields.append('max_text_length')
            else:
                raise HTTPException(status_code=400, detail="max_text_length必须大于0")
        
        # 更新自动清理配置
        if config_update.auto_cleanup is not None:
            parser_config.TEMP_FILE_CONFIG['auto_cleanup'] = config_update.auto_cleanup
            updated_fields.append('auto_cleanup')
        
        if not updated_fields:
            raise HTTPException(status_code=400, detail="没有提供有效的配置更新")
        
        logger.info(f"配置更新成功，更新字段: {updated_fields}")
        
        return {
            "success": True,
            "message": "配置更新成功",
            "updated_fields": updated_fields,
            "current_config": {
                "max_pages_per_batch": parser_config.get_max_pages_per_batch(),
                "pdf_strategy": parser_config.PARSER_STRATEGIES['pdf']['strategy'],
                "include_page_breaks": parser_config.PARSER_STRATEGIES['pdf']['include_page_breaks'],
                "infer_table_structure": parser_config.PARSER_STRATEGIES['pdf']['infer_table_structure'],
                "max_text_length": parser_config.TEXT_EXTRACTION_CONFIG['max_text_length'],
                "auto_cleanup": parser_config.TEMP_FILE_CONFIG['auto_cleanup']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@config_router.post("/parser/reset", summary="重置配置为默认值")
async def reset_parser_config() -> Dict[str, Any]:
    """重置解析器配置为默认值
    
    Returns:
        Dict[str, Any]: 重置结果
    """
    try:
        # 重置为默认配置
        parser_config.PDF_BATCH_CONFIG['max_pages_per_batch'] = 5
        parser_config.PARSER_STRATEGIES['pdf']['strategy'] = 'auto'
        parser_config.PARSER_STRATEGIES['pdf']['include_page_breaks'] = True
        parser_config.PARSER_STRATEGIES['pdf']['infer_table_structure'] = True
        parser_config.PARSER_STRATEGIES['docx']['include_page_breaks'] = True
        parser_config.PARSER_STRATEGIES['docx']['infer_table_structure'] = True
        parser_config.TEXT_EXTRACTION_CONFIG['max_text_length'] = 1000000
        parser_config.TEMP_FILE_CONFIG['auto_cleanup'] = True
        
        logger.info("配置已重置为默认值")
        
        return {
            "success": True,
            "message": "配置已重置为默认值",
            "default_config": {
                "max_pages_per_batch": 5,
                "pdf_strategy": "auto",
                "include_page_breaks": True,
                "infer_table_structure": True,
                "max_text_length": 1000000,
                "auto_cleanup": True
            }
        }
        
    except Exception as e:
        logger.error(f"重置配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"重置配置失败: {str(e)}")