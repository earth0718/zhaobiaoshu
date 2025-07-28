#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标书文档解析系统主应用

集成文档解析功能的FastAPI应用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import os
from contextlib import asynccontextmanager

# 导入文档解析API
from src.parser.api import router as document_router
from src.parser.config_api import config_router
from src.parser import get_module_info

# 导入招标生成API
from src.tender_generation_core.api import router as tender_router

# 导入历史记录API
from src.history.api import router as history_router

# 导入过滤器API
from src.api.filter import router as filter_router
# 导入招标书生成API
from src.gender_book.api import router as gender_book_router

# 配置日志 - 只输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("招标书文档解析系统启动中...")
    
    # 检查文档解析模块
    try:
        module_info = get_module_info()
        logger.info(f"文档解析模块已加载: {module_info['name']} v{module_info['version']}")
        logger.info(f"支持的文件格式: {list(module_info['supported_formats'].keys())}")
    except Exception as e:
        logger.error(f"文档解析模块加载失败: {str(e)}")
    
    yield
    
    # 关闭时的清理
    logger.info("招标书文档解析系统关闭")


# 创建FastAPI应用
app = FastAPI(
    title="招标书文档解析系统",
    description="基于unstructured库的文档解析系统，支持PDF、Word、TXT等格式文件的解析和JSON转换",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "message": "请联系系统管理员",
            "detail": str(exc) if app.debug else None
        }
    )


# 注册路由
app.include_router(document_router, prefix="/api/parser", tags=["文档解析"])
app.include_router(config_router, prefix="/api/config", tags=["配置管理"])
app.include_router(tender_router, prefix="/api/tender", tags=["招标文件生成"])
app.include_router(history_router, prefix="/api/history", tags=["历史记录"])
app.include_router(filter_router, tags=["过滤器"])
app.include_router(gender_book_router, tags=["招标书生成"])

# 挂载静态文件服务（前端界面）
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    logger.info(f"前端静态文件已挂载: {frontend_path}")

# 挂载配置文件服务
config_path = os.path.join(os.path.dirname(__file__), "config")
if os.path.exists(config_path):
    app.mount("/config", StaticFiles(directory=config_path), name="config")
    logger.info(f"配置文件已挂载: {config_path}")


# 根路径 - 重定向到前端界面
@app.get("/", tags=["系统信息"])
async def root():
    """系统根路径，重定向到前端界面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

# 系统信息API
@app.get("/api/info", tags=["系统信息"])
async def api_info():
    """获取系统API信息"""
    try:
        module_info = get_module_info()
        return {
            "message": "欢迎使用招标书文档解析系统",
            "system": {
                "name": "招标书文档解析系统",
                "version": "1.0.0",
                "description": "基于unstructured库的文档解析系统"
            },
            "parser_module": {
                "name": module_info['name'],
                "version": module_info['version'],
                "supported_formats": list(module_info['supported_formats'].keys())
            },
            "api_docs": {
                "swagger_ui": "/docs",
                "redoc": "/redoc"
            },
            "endpoints": {
                "parse_document": "/api/parser/parse",
                "batch_parse": "/api/parser/parse/batch",
                "extract_text": "/api/parser/extract/text",
                "extract_structured": "/api/parser/extract/structured",
                "supported_formats": "/api/parser/formats",
                "health_check": "/api/parser/health",
                "generate_tender": "/api/tender/generate",
                "tender_status": "/api/tender/status/{task_id}",
                "tender_models": "/api/tender/models",
                "tender_health": "/api/tender/health",
                "history_records": "/api/history/records",
                "history_statistics": "/api/history/statistics",
                "history_export": "/api/history/export/{record_id}"
            }
        }
    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取系统信息失败")


@app.get("/health", tags=["系统信息"])
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "document_parser": "running",
            "api": "running"
        }
    }


@app.get("/info", tags=["系统信息"])
async def system_info():
    """获取详细的系统信息"""
    try:
        module_info = get_module_info()
        return {
            "system": {
                "name": "招标书文档解析系统",
                "version": "1.0.0",
                "description": "基于unstructured库的文档解析系统，支持多种文档格式的解析和转换"
            },
            "features": [
                "PDF文档解析",
                "Word文档解析",
                "文本文件解析",
                "批量文档处理",
                "结构化数据提取",
                "纯文本提取",
                "JSON格式输出"
            ],
            "supported_formats": module_info['supported_formats'],
            "parser_info": {
                "library": "unstructured",
                "version": module_info['version'],
                "capabilities": [
                    "自动文档类型检测",
                    "表格结构识别",
                    "元数据提取",
                    "多种解析策略"
                ]
            },
            "api_info": {
                "framework": "FastAPI",
                "documentation": "/docs",
                "base_url": "/api/parser"
            }
        }
    except Exception as e:
        logger.error(f"获取系统详细信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取系统信息失败")


if __name__ == "__main__":
    import uvicorn
    
    # 开发环境配置
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )