#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化模块

功能说明：
- 提供文档处理性能优化功能
- 实现内容去重和合并优化
- 提供缓存机制以提高处理效率
- 优化大文档的内存使用
"""

import hashlib
import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict


def calculate_text_hash(text: str) -> str:
    """计算文本的哈希值用于去重"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def remove_duplicate_content(document_contents: Dict[str, str]) -> Dict[str, str]:
    """移除重复的文档内容
    
    Args:
        document_contents: 文档内容字典
        
    Returns:
        Dict[str, str]: 去重后的文档内容字典
    """
    if len(document_contents) <= 1:
        return document_contents
    
    # 计算每个文档的哈希值
    content_hashes = {}
    hash_to_filename = {}
    
    for filename, content in document_contents.items():
        content_hash = calculate_text_hash(content)
        content_hashes[filename] = content_hash
        
        if content_hash in hash_to_filename:
            print(f"发现重复文档: {filename} 与 {hash_to_filename[content_hash]} 内容相同")
        else:
            hash_to_filename[content_hash] = filename
    
    # 保留每个唯一内容的第一个文档
    unique_contents = {}
    seen_hashes = set()
    
    for filename, content in document_contents.items():
        content_hash = content_hashes[filename]
        if content_hash not in seen_hashes:
            unique_contents[filename] = content
            seen_hashes.add(content_hash)
    
    if len(unique_contents) < len(document_contents):
        removed_count = len(document_contents) - len(unique_contents)
        print(f"已移除 {removed_count} 个重复文档")
    
    return unique_contents


def detect_similar_sections(document_contents: Dict[str, str], similarity_threshold: float = 0.8) -> List[Tuple[str, str, float]]:
    """检测文档间的相似章节
    
    Args:
        document_contents: 文档内容字典
        similarity_threshold: 相似度阈值
        
    Returns:
        List[Tuple[str, str, float]]: 相似章节列表 (文档1, 文档2, 相似度)
    """
    similar_sections = []
    filenames = list(document_contents.keys())
    
    for i in range(len(filenames)):
        for j in range(i + 1, len(filenames)):
            file1, file2 = filenames[i], filenames[j]
            content1, content2 = document_contents[file1], document_contents[file2]
            
            # 简单的相似度计算（基于共同词汇）
            similarity = calculate_content_similarity(content1, content2)
            
            if similarity >= similarity_threshold:
                similar_sections.append((file1, file2, similarity))
    
    return similar_sections


def calculate_content_similarity(content1: str, content2: str) -> float:
    """计算两个文档内容的相似度
    
    Args:
        content1: 文档1内容
        content2: 文档2内容
        
    Returns:
        float: 相似度 (0-1)
    """
    # 简单的基于词汇重叠的相似度计算
    words1 = set(re.findall(r'\w+', content1.lower()))
    words2 = set(re.findall(r'\w+', content2.lower()))
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def optimize_content_structure(merged_content: str) -> str:
    """优化合并后的内容结构
    
    Args:
        merged_content: 合并后的内容
        
    Returns:
        str: 优化后的内容
    """
    lines = merged_content.split('\n')
    optimized_lines = []
    
    # 移除过多的空行
    consecutive_empty_lines = 0
    for line in lines:
        if line.strip() == '':
            consecutive_empty_lines += 1
            if consecutive_empty_lines <= 2:  # 最多保留2个连续空行
                optimized_lines.append(line)
        else:
            consecutive_empty_lines = 0
            optimized_lines.append(line)
    
    # 标准化分隔符
    content = '\n'.join(optimized_lines)
    content = re.sub(r'-{3,}', '---', content)  # 标准化分隔线
    content = re.sub(r'={3,}', '===', content)  # 标准化等号分隔线
    
    return content


def extract_key_sections(content: str) -> Dict[str, str]:
    """提取文档中的关键章节
    
    Args:
        content: 文档内容
        
    Returns:
        Dict[str, str]: 章节标题到内容的映射
    """
    sections = {}
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    # 定义章节标题的模式
    section_patterns = [
        r'^#+\s+(.+)$',  # Markdown标题
        r'^第[一二三四五六七八九十\d]+章\s+(.+)$',  # 中文章节
        r'^第[一二三四五六七八九十\d]+节\s+(.+)$',  # 中文小节
        r'^\d+\.\s+(.+)$',  # 数字编号
        r'^[一二三四五六七八九十]、\s*(.+)$',  # 中文编号
    ]
    
    for line in lines:
        line = line.strip()
        
        # 检查是否是章节标题
        is_section_title = False
        for pattern in section_patterns:
            match = re.match(pattern, line)
            if match:
                # 保存前一个章节
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # 开始新章节
                current_section = match.group(1).strip()
                current_content = []
                is_section_title = True
                break
        
        if not is_section_title and line:
            current_content.append(line)
    
    # 保存最后一个章节
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def merge_similar_sections(sections: Dict[str, str], similarity_threshold: float = 0.7) -> Dict[str, str]:
    """合并相似的章节
    
    Args:
        sections: 章节字典
        similarity_threshold: 相似度阈值
        
    Returns:
        Dict[str, str]: 合并后的章节字典
    """
    if len(sections) <= 1:
        return sections
    
    merged_sections = {}
    processed_sections = set()
    section_items = list(sections.items())
    
    for i, (title1, content1) in enumerate(section_items):
        if title1 in processed_sections:
            continue
        
        # 查找相似的章节
        similar_sections = [(title1, content1)]
        
        for j, (title2, content2) in enumerate(section_items[i+1:], i+1):
            if title2 in processed_sections:
                continue
            
            # 计算标题相似度
            title_similarity = calculate_content_similarity(title1, title2)
            content_similarity = calculate_content_similarity(content1, content2)
            
            overall_similarity = (title_similarity + content_similarity) / 2
            
            if overall_similarity >= similarity_threshold:
                similar_sections.append((title2, content2))
                processed_sections.add(title2)
        
        # 合并相似章节
        if len(similar_sections) > 1:
            merged_title = similar_sections[0][0]  # 使用第一个标题
            merged_content = '\n\n'.join([content for _, content in similar_sections])
            merged_sections[f"{merged_title} (合并章节)"] = merged_content
        else:
            merged_sections[title1] = content1
        
        processed_sections.add(title1)
    
    return merged_sections


def optimize_document_processing(document_contents: Dict[str, str]) -> Dict[str, str]:
    """综合优化文档处理
    
    Args:
        document_contents: 原始文档内容字典
        
    Returns:
        Dict[str, str]: 优化后的文档内容字典
    """
    print("开始性能优化处理...")
    
    # 1. 移除重复内容
    print("1. 移除重复文档...")
    unique_contents = remove_duplicate_content(document_contents)
    
    # 2. 检测相似章节
    print("2. 检测相似章节...")
    similar_sections = detect_similar_sections(unique_contents)
    if similar_sections:
        print(f"发现 {len(similar_sections)} 对相似章节")
        for file1, file2, similarity in similar_sections:
            print(f"  - {file1} 与 {file2} 相似度: {similarity:.2f}")
    
    # 3. 优化每个文档的内容结构
    print("3. 优化内容结构...")
    optimized_contents = {}
    for filename, content in unique_contents.items():
        optimized_content = optimize_content_structure(content)
        optimized_contents[filename] = optimized_content
    
    print("性能优化处理完成")
    return optimized_contents


class ContentCache:
    """内容缓存类"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.access_order = []
        self.max_size = max_size
    
    def get(self, key: str) -> str:
        """获取缓存内容"""
        if key in self.cache:
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: str):
        """存储缓存内容"""
        if key in self.cache:
            # 更新现有缓存
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # 移除最久未使用的缓存
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_order.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)


# 全局缓存实例
content_cache = ContentCache(max_size=50)