#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档解析API模块
提供文档上传和解析的RESTful API接口
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from .document_service import get_document_service, DocumentService
from .document_parser import DocumentParseError

# 请求模型
class ParseConfig(BaseModel):
    """解析配置模型"""
    max_pages_per_batch: int = 5
    include_metadata: bool = True

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/document", tags=["文档解析"])


# Pydantic模型定义
class DocumentParseResponse(BaseModel):
    """文档解析响应模型"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="响应消息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="解析结果数据")
    error: Optional[str] = Field(default=None, description="错误信息")


class BatchParseResponse(BaseModel):
    """批量解析响应模型"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="响应消息")
    total_files: int = Field(description="总文件数")
    successful_files: int = Field(description="成功解析的文件数")
    failed_files: int = Field(description="解析失败的文件数")
    results: List[Dict[str, Any]] = Field(description="详细结果列表")


class SupportedFormatsResponse(BaseModel):
    """支持格式响应模型"""
    supported_extensions: List[str] = Field(description="支持的文件扩展名")
    supported_types: List[str] = Field(description="支持的文件类型")
    format_mapping: Dict[str, str] = Field(description="扩展名到类型的映射")


class FileValidationResponse(BaseModel):
    """文件验证响应模型"""
    filename: str = Field(description="文件名")
    extension: str = Field(description="文件扩展名")
    is_supported: bool = Field(description="是否支持")
    file_type: Optional[str] = Field(description="文件类型")
    supported_formats: SupportedFormatsResponse = Field(description="支持的格式信息")


@router.post("/parse", response_model=DocumentParseResponse, summary="解析单个文档")
async def parse_document(
    file: UploadFile = File(..., description="要解析的文档文件"),
    include_metadata: bool = Query(True, description="是否包含元数据"),
    cleanup: bool = Query(True, description="是否清理临时文件"),
    max_pages_per_batch: int = Query(5, description="PDF分页处理时每批处理的最大页数", ge=1, le=20)
):
    """
    解析单个文档文件
    
    支持的文件格式:
    - PDF (.pdf)
    - Word文档 (.docx, .doc)
    - 文本文件 (.txt, .md)
    
    Args:
        file: 上传的文档文件
        include_metadata: 是否在结果中包含元数据信息
        max_pages_per_batch: PDF分页处理时每批处理的最大页数
        
    Returns:
        解析结果，包含文档信息和提取的内容
    """
    try:
        # 获取文档服务实例
        service = get_document_service(max_pages_per_batch=max_pages_per_batch)
        
        # 验证文件类型
        if not service.is_supported_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.filename}"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        # 解析文档
        result = service.parse_uploaded_file(
            file_content=file_content,
            filename=file.filename,
            include_metadata=include_metadata,
            cleanup=cleanup
        )
        
        return DocumentParseResponse(
            success=True,
            message="文档解析成功",
            data={
                **result,
                "config": {
                    "max_pages_per_batch": max_pages_per_batch,
                    "include_metadata": include_metadata
                }
            }
        )
        
    except DocumentParseError as e:
        logger.error(f"文档解析失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/parse/batch", response_model=BatchParseResponse, summary="批量解析文档")
async def batch_parse_documents(
    files: List[UploadFile] = File(..., description="要解析的文档文件列表"),
    include_metadata: bool = Query(True, description="是否包含元数据"),
    cleanup: bool = Query(True, description="是否清理临时文件"),
    max_pages_per_batch: int = Query(5, description="PDF分页处理时每批处理的最大页数", ge=1, le=20)
):
    """
    批量解析多个文档文件
    
    Args:
        files: 上传的文档文件列表
        include_metadata: 是否在结果中包含元数据信息
        max_pages_per_batch: PDF分页处理时每批处理的最大页数
        
    Returns:
        批量解析结果，包含成功和失败的文件信息
    """
    try:
        # 获取文档服务实例
        service = get_document_service(max_pages_per_batch=max_pages_per_batch)
        
        # 准备文件数据
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append({
                'content': content,
                'filename': file.filename
            })
        
        # 批量解析文档
        results = service.batch_parse_files(
            file_data,
            include_metadata=include_metadata,
            cleanup=cleanup
        )
        
        # 统计结果
        successful_files = sum(1 for r in results if r['success'])
        failed_files = len(results) - successful_files
        
        logger.info(f"批量解析完成: 总计 {len(files)} 个文件，成功 {successful_files} 个，失败 {failed_files} 个")
        
        return BatchParseResponse(
            success=True,
            message=f"批量解析完成，成功 {successful_files}/{len(files)} 个文件",
            total_files=len(files),
            successful_files=successful_files,
            failed_files=failed_files,
            results=[
                {
                    **result,
                    "config": {
                        "max_pages_per_batch": max_pages_per_batch,
                        "include_metadata": include_metadata
                    }
                } for result in results
            ]
        )
        
    except Exception as e:
        logger.error(f"批量解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="批量解析失败")


@router.post("/extract/text", response_model=DocumentParseResponse, summary="提取纯文本")
async def extract_text(
    file: UploadFile = File(..., description="要提取文本的文档文件"),
    max_length: Optional[int] = Query(None, description="最大文本长度，超出部分将被截断")
):
    """
    从文档中提取纯文本内容
    
    返回文档的纯文本内容，可选择限制最大长度
    """
    try:
        service = get_document_service()
        
        # 验证文件类型
        validation = service.validate_file(file.filename)
        if not validation['is_supported']:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {validation['extension']}"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        # 提取文本
        result = service.extract_text_summary(
            file_content=file_content,
            filename=file.filename,
            max_length=max_length
        )
        
        logger.info(f"成功提取文本: {file.filename}")
        
        return DocumentParseResponse(
            success=True,
            message="文本提取成功",
            data=result
        )
        
    except DocumentParseError as e:
        logger.error(f"文本提取失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"服务器内部错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/extract/structured", response_model=DocumentParseResponse, summary="提取结构化数据")
async def extract_structured_data(
    file: UploadFile = File(..., description="要提取结构化数据的文档文件"),
    target_types: Optional[str] = Query(
        None, 
        description="目标元素类型，多个类型用逗号分隔，如: Title,Table,List"
    )
):
    """
    从文档中提取结构化数据
    
    可以指定要提取的元素类型，如标题、表格、列表等
    常见的元素类型包括：Title, Header, Text, Table, List, Image等
    """
    try:
        service = get_document_service()
        
        # 验证文件类型
        validation = service.validate_file(file.filename)
        if not validation['is_supported']:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {validation['extension']}"
            )
        
        # 解析目标类型
        target_type_list = None
        if target_types:
            target_type_list = [t.strip() for t in target_types.split(',') if t.strip()]
        
        # 读取文件内容
        file_content = await file.read()
        
        # 提取结构化数据
        result = service.extract_structured_data(
            file_content=file_content,
            filename=file.filename,
            target_types=target_type_list
        )
        
        logger.info(f"成功提取结构化数据: {file.filename}")
        
        return DocumentParseResponse(
            success=True,
            message="结构化数据提取成功",
            data=result
        )
        
    except DocumentParseError as e:
        logger.error(f"结构化数据提取失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"服务器内部错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/formats", response_model=SupportedFormatsResponse, summary="获取支持的文件格式")
async def get_supported_formats():
    """
    获取支持的文件格式信息
    
    返回所有支持的文件扩展名、类型和映射关系
    """
    try:
        service = get_document_service()
        formats = service.get_supported_formats()
        
        return SupportedFormatsResponse(**formats)
        
    except Exception as e:
        logger.error(f"获取支持格式失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取支持格式失败")


@router.get("/validate/{filename}", response_model=FileValidationResponse, summary="验证文件格式")
async def validate_file_format(filename: str):
    """
    验证指定文件名的格式是否支持
    
    Args:
        filename: 要验证的文件名
    
    Returns:
        文件验证结果，包括是否支持、文件类型等信息
    """
    try:
        service = get_document_service()
        validation = service.validate_file(filename)
        
        return FileValidationResponse(**validation)
        
    except Exception as e:
        logger.error(f"文件验证失败: {str(e)}")
        raise HTTPException(status_code=500, detail="文件验证失败")


@router.get("/health", summary="健康检查")
async def health_check():
    """
    API健康检查接口
    
    返回服务状态和基本信息
    """
    try:
        service = get_document_service()
        formats = service.get_supported_formats()
        
        return {
            "status": "healthy",
            "service": "文档解析服务",
            "version": "1.0.0",
            "supported_formats": len(formats['supported_extensions']),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务不可用")