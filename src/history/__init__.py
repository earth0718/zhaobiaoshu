#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标书生成历史记录模块

功能说明：
- 管理招标书生成的历史记录
- 自动保存最近20条生成记录
- 提供历史记录查询和管理接口
- 支持历史记录的导出和清理
"""

from .history_manager import HistoryManager
from .models import TenderHistoryRecord, HistoryQueryParams

__all__ = ['HistoryManager', 'TenderHistoryRecord', 'HistoryQueryParams']