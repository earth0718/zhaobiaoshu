#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录API接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .history_manager import history_manager
from .models import HistoryQueryParams, HistoryListResponse, HistoryStatsResponse, TenderHistoryRecord

router = APIRouter()

@router.get("/records", response_model=HistoryListResponse, summary="获取历史记录列表")
async def get_history_records(
    limit: Optional[int] = Query(20, ge=1, le=100, description="每页记录数"),
    offset: Optional[int] = Query(0, ge=0, description="偏移量"),
    status: Optional[str] = Query(None, description="状态过滤 (completed/failed)"),
    model: Optional[str] = Query(None, description="模型过滤"),
    date_from: Optional[str] = Query(None, description="开始日期 (ISO格式)"),
    date_to: Optional[str] = Query(None, description="结束日期 (ISO格式)")
):
    """
    获取招标文件生成历史记录列表
    
    支持分页和多种过滤条件：
    - 按状态过滤（成功/失败）
    - 按模型过滤
    - 按日期范围过滤
    """
    try:
        params = HistoryQueryParams(
            limit=limit,
            offset=offset,
            status_filter=status,
            model_filter=model,
            date_from=date_from,
            date_to=date_to
        )
        
        return history_manager.get_records(params)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

@router.get("/records/{record_id}", response_model=TenderHistoryRecord, summary="获取单个历史记录")
async def get_history_record(record_id: str):
    """
    根据记录ID获取单个历史记录详情
    """
    try:
        record = history_manager.get_record_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        return record
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记录失败: {str(e)}")

@router.delete("/records/{record_id}", summary="删除历史记录")
async def delete_history_record(record_id: str):
    """
    删除指定的历史记录
    """
    try:
        success = history_manager.delete_record(record_id)
        if not success:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        return {"message": "记录删除成功", "record_id": record_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除记录失败: {str(e)}")

@router.get("/statistics", response_model=HistoryStatsResponse, summary="获取历史记录统计")
async def get_history_statistics():
    """
    获取历史记录统计信息
    
    包括：
    - 总记录数
    - 成功/失败数量
    - 最常用模型
    - 平均处理时间
    - 最新生成时间
    """
    try:
        return history_manager.get_statistics()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.delete("/records", summary="清空所有历史记录")
async def clear_all_history():
    """
    清空所有历史记录
    
    注意：此操作不可逆
    """
    try:
        count = history_manager.clear_all_records()
        return {"message": f"已清空 {count} 条历史记录"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空记录失败: {str(e)}")

@router.get("/export/{record_id}", summary="导出历史记录")
async def export_history_record(record_id: str):
    """
    导出指定历史记录的招标书内容
    """
    try:
        record = history_manager.get_record_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        from fastapi.responses import Response
        import urllib.parse
        
        # 获取招标书内容，如果为空则使用摘要
        content = record.tender_content
        if not content or content.strip() == "":
            content = record.tender_summary or "招标书内容为空"
        
        # 确保内容不为None
        if content is None:
            content = "招标书内容为空"
        
        # 使用安全的文件名，避免中文编码问题
        safe_filename = f"tender_document_{record_id}_{record.generation_time[:10]}.md"
        encoded_filename = urllib.parse.quote(safe_filename)
        
        return Response(
            content=content.encode('utf-8'),
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出记录失败: {str(e)}")