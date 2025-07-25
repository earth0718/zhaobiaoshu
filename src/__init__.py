# src/__init__.py
"""招标书智能生成系统核心模块"""

__version__ = "1.0.0"
__author__ = "招标文件生成系统开发团队"

# 避免循环导入，不在此处导入子模块
__all__ = [
    "parser",
    "llm",
    "tender",
]