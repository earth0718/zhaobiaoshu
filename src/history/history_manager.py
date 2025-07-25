#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标书生成历史记录管理器
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from .models import TenderHistoryRecord, HistoryQueryParams, HistoryListResponse, HistoryStatsResponse

class HistoryManager:
    """招标书生成历史记录管理器"""
    
    def __init__(self, history_dir: str = "src/history", max_records: int = 20):
        self.history_dir = Path(history_dir)
        self.max_records = max_records
        self.records_file = self.history_dir / "records.json"
        self.content_dir = self.history_dir / "content"
        
        # 确保目录存在
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.content_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化记录文件
        if not self.records_file.exists():
            self._save_records([])
    
    def _load_records(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_records(self, records: List[Dict[str, Any]]):
        """保存历史记录"""
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    def _save_content_to_file(self, record_id: str, content: str) -> str:
        """保存招标书内容到文件"""
        content_file = self.content_dir / f"{record_id}.txt"
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(content_file)
    
    def _load_content_from_file(self, file_path: str) -> Optional[str]:
        """从文件加载招标书内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """生成内容摘要"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
    
    def add_record(self, 
                   task_id: str,
                   original_filename: str,
                   file_size: int,
                   model_provider: str,
                   quality_level: str,
                   tender_content: str,
                   status: str = "completed",
                   error_message: Optional[str] = None,
                   processing_duration: Optional[float] = None) -> str:
        """添加新的历史记录"""
        
        record_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # 保存招标书内容到文件
        content_file_path = self._save_content_to_file(record_id, tender_content)
        
        # 创建记录
        record = {
            "record_id": record_id,
            "task_id": task_id,
            "original_filename": original_filename,
            "file_size": file_size,
            "model_provider": model_provider,
            "quality_level": quality_level,
            "generation_time": current_time,
            "processing_duration": processing_duration,
            "status": status,
            "error_message": error_message,
            "tender_content": tender_content if len(tender_content) <= 1000 else "",  # 只保存短内容
            "tender_summary": self._generate_summary(tender_content),
            "created_at": current_time,
            "file_path": content_file_path
        }
        
        # 加载现有记录
        records = self._load_records()
        
        # 添加新记录到开头
        records.insert(0, record)
        
        # 保持最大记录数限制
        if len(records) > self.max_records:
            # 删除超出限制的记录及其文件
            for old_record in records[self.max_records:]:
                if old_record.get("file_path") and os.path.exists(old_record["file_path"]):
                    try:
                        os.remove(old_record["file_path"])
                    except OSError:
                        pass
            
            records = records[:self.max_records]
        
        # 保存更新后的记录
        self._save_records(records)
        
        return record_id
    
    def get_records(self, params: HistoryQueryParams) -> HistoryListResponse:
        """获取历史记录列表"""
        records = self._load_records()
        
        # 应用过滤器
        filtered_records = records
        
        if params.status_filter:
            filtered_records = [r for r in filtered_records if r.get("status") == params.status_filter]
        
        if params.model_filter:
            filtered_records = [r for r in filtered_records if r.get("model_provider") == params.model_filter]
        
        if params.date_from:
            filtered_records = [r for r in filtered_records if r.get("created_at", "") >= params.date_from]
        
        if params.date_to:
            filtered_records = [r for r in filtered_records if r.get("created_at", "") <= params.date_to]
        
        # 分页
        total_count = len(filtered_records)
        start_idx = params.offset or 0
        end_idx = start_idx + (params.limit or 20)
        
        paginated_records = filtered_records[start_idx:end_idx]
        
        # 转换为模型对象
        record_objects = []
        for record_data in paginated_records:
            # 如果内容为空，尝试从文件加载
            if not record_data.get("tender_content") and record_data.get("file_path"):
                content = self._load_content_from_file(record_data["file_path"])
                if content:
                    record_data["tender_content"] = content
            
            record_objects.append(TenderHistoryRecord(**record_data))
        
        return HistoryListResponse(
            total_count=total_count,
            records=record_objects,
            has_more=end_idx < total_count
        )
    
    def get_record_by_id(self, record_id: str) -> Optional[TenderHistoryRecord]:
        """根据ID获取单个记录"""
        records = self._load_records()
        
        for record_data in records:
            if record_data.get("record_id") == record_id:
                # 如果内容为空，尝试从文件加载
                if not record_data.get("tender_content") and record_data.get("file_path"):
                    content = self._load_content_from_file(record_data["file_path"])
                    if content:
                        record_data["tender_content"] = content
                
                return TenderHistoryRecord(**record_data)
        
        return None
    
    def delete_record(self, record_id: str) -> bool:
        """删除指定记录"""
        records = self._load_records()
        
        for i, record in enumerate(records):
            if record.get("record_id") == record_id:
                # 删除内容文件
                if record.get("file_path") and os.path.exists(record["file_path"]):
                    try:
                        os.remove(record["file_path"])
                    except OSError:
                        pass
                
                # 从列表中移除
                records.pop(i)
                self._save_records(records)
                return True
        
        return False
    
    def get_statistics(self) -> HistoryStatsResponse:
        """获取历史记录统计信息"""
        records = self._load_records()
        
        if not records:
            return HistoryStatsResponse(
                total_records=0,
                completed_count=0,
                failed_count=0,
                most_used_model="N/A"
            )
        
        completed_count = len([r for r in records if r.get("status") == "completed"])
        failed_count = len([r for r in records if r.get("status") == "failed"])
        
        # 统计最常用模型
        model_counts = {}
        processing_times = []
        
        for record in records:
            model = record.get("model_provider", "unknown")
            model_counts[model] = model_counts.get(model, 0) + 1
            
            if record.get("processing_duration"):
                processing_times.append(record["processing_duration"])
        
        most_used_model = max(model_counts.items(), key=lambda x: x[1])[0] if model_counts else "N/A"
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else None
        latest_generation = records[0].get("created_at") if records else None
        
        return HistoryStatsResponse(
            total_records=len(records),
            completed_count=completed_count,
            failed_count=failed_count,
            most_used_model=most_used_model,
            average_processing_time=avg_processing_time,
            latest_generation=latest_generation
        )
    
    def clear_all_records(self) -> int:
        """清空所有历史记录"""
        records = self._load_records()
        count = len(records)
        
        # 删除所有内容文件
        for record in records:
            if record.get("file_path") and os.path.exists(record["file_path"]):
                try:
                    os.remove(record["file_path"])
                except OSError:
                    pass
        
        # 清空记录
        self._save_records([])
        
        return count

# 全局历史管理器实例
history_manager = HistoryManager()