from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.filter import process_tender_document_optimized

router = APIRouter(prefix="/api/filter", tags=["filter"])
logger = logging.getLogger(__name__)

class FilterRequest(BaseModel):
    """过滤请求模型"""
    content: Any  # 可以是任何JSON结构
    
class FilterResponse(BaseModel):
    """过滤响应模型"""
    success: bool
    data: Dict[str, Any]
    message: str = ""
    error: str = ""

@router.post("/process", response_model=FilterResponse)
async def process_json_filter(request: Dict[str, Any]):
    """
    处理JSON文件过滤
    
    Args:
        request: 包含需要过滤的JSON数据的请求
        
    Returns:
        FilterResponse: 过滤后的数据
    """
    try:
        logger.info("开始处理JSON过滤请求")
        
        # 验证输入数据
        if not request:
            raise HTTPException(status_code=400, detail="请求数据不能为空")
        
        # 调用智能处理函数
        result = process_tender_document_optimized(request)
        
        if not result:
            raise HTTPException(status_code=500, detail="智能处理失败，返回数据为空")
        
        logger.info(f"JSON智能处理完成，原始数据大小: {len(str(request))}, 处理后数据大小: {len(str(result.get('optimized_data', {})))}")
        
        return FilterResponse(
            success=True,
            data=result,
            message="JSON文件智能处理完成"
        )
        
    except Exception as e:
        logger.error(f"JSON过滤处理失败: {str(e)}")
        return FilterResponse(
            success=False,
            data={},
            error=f"处理失败: {str(e)}"
        )

@router.get("/health")
async def filter_health():
    """
    过滤器模块健康检查
    """
    try:
        # 简单测试智能处理函数是否可用
        test_data = {"content": [{"text": "test", "type": "text"}]}
        process_tender_document_optimized(test_data)
        
        return {
            "status": "healthy",
            "module": "filter",
            "message": "智能处理模块运行正常"
        }
    except Exception as e:
        logger.error(f"智能处理模块健康检查失败: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"智能处理模块不可用: {str(e)}"
        )