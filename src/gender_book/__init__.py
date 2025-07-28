# gender_book模块 - 招标书分章节生成系统
"""
招标书分章节生成模块

该模块提供了一个完整的招标书生成系统，能够：
1. 处理经过filter.py过滤的JSON数据
2. 智能分析JSON内容并生成章节结构
3. 分章节生成招标书内容，适合小模型处理
4. 提供完整的API接口

主要组件：
- section_manager.py: 章节管理器，负责分析和生成章节结构
- tender_generator.py: 招标书生成器，负责具体内容生成
- api.py: API接口，提供REST服务
"""

__version__ = "1.0.0"
__author__ = "招标书生成系统"

__all__ = [
    "SectionManager",
    "TenderGenerator", 
    "router"
]