#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF分页处理功能
"""

import asyncio
from pathlib import Path
from src.parser.document_parser import DocumentParser
from src.parser.document_service import DocumentService
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_pagination():
    """测试PDF分页处理"""
    
    # 创建解析器实例，设置每批处理2页
    parser = DocumentParser(max_pages_per_batch=2)
    
    # 测试文件路径（请替换为实际的PDF文件路径）
    test_pdf = Path("test.pdf")
    
    if not test_pdf.exists():
        logger.warning(f"测试文件不存在: {test_pdf}")
        logger.info("请将一个PDF文件命名为'test.pdf'并放在项目根目录下进行测试")
        return
    
    try:
        logger.info("开始测试PDF分页处理...")
        
        # 解析PDF
        result = parser.parse_to_json(
            file_path=test_pdf,
            include_metadata=True
        )
        
        logger.info(f"解析完成！")
        logger.info(f"文档信息: {result['document_info']}")
        logger.info(f"提取的元素数量: {len(result['content'])}")
        
        # 显示前几个元素的信息
        for i, element in enumerate(result['content'][:5]):
            logger.info(f"元素 {i+1}: 类型={element['type']}, 文本长度={len(element['text'])}, 页面={element.get('metadata', {}).get('page_number', 'N/A')}")
        
        return result
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        return None

def test_service_pagination():
    """测试服务层的分页处理"""
    
    # 创建服务实例
    service = DocumentService(max_pages_per_batch=3)
    
    test_pdf = Path("test.pdf")
    
    if not test_pdf.exists():
        logger.warning(f"测试文件不存在: {test_pdf}")
        return
    
    try:
        logger.info("开始测试服务层分页处理...")
        
        # 使用服务解析
        result = service.parse_file(
            file_path=test_pdf,
            include_metadata=True
        )
        
        logger.info(f"服务层解析完成！")
        logger.info(f"提取的结构化数据元素数量: {len(result.get('structured_data', []))}")
        logger.info(f"文本摘要长度: {len(result.get('text_summary', ''))}")
        
        return result
        
    except Exception as e:
        logger.error(f"服务层测试失败: {str(e)}")
        return None

def main():
    """主测试函数"""
    logger.info("=== PDF分页处理功能测试 ===")
    
    # 测试1: 基础解析器
    logger.info("\n1. 测试基础解析器分页功能")
    result1 = test_pdf_pagination()
    
    # 测试2: 服务层
    logger.info("\n2. 测试服务层分页功能")
    result2 = test_service_pagination()
    
    if result1 or result2:
        logger.info("\n✅ 测试完成！分页处理功能正常工作")
    else:
        logger.info("\n❌ 测试失败，请检查错误信息")

if __name__ == "__main__":
    main()