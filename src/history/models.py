#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录数据模型
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class TenderHistoryRecord(BaseModel):
    """招标书生成历史记录模型"""
    record_id: str
    task_id: str
    original_filename: str
    file_size: int
    model_provider: str
    quality_level: str
    generation_time: str
    processing_duration: Optional[float] = None  # 处理耗时（秒）
    status: str  # completed, failed
    error_message: Optional[str] = None
    tender_content: str
    tender_summary: Optional[str] = None
    created_at: str
    file_path: Optional[str] = None  # 保存的文件路径
    
class HistoryQueryParams(BaseModel):
    """历史记录查询参数"""
    limit: Optional[int] = 20
    offset: Optional[int] = 0
    status_filter: Optional[str] = None  # completed, failed
    model_filter: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    
class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    total_count: int
    records: List[TenderHistoryRecord]
    has_more: bool
    
class HistoryStatsResponse(BaseModel):
    """历史记录统计响应"""
    total_records: int
    completed_count: int
    failed_count: int
    most_used_model: str
    average_processing_time: Optional[float] = None
    latest_generation: Optional[str] = None