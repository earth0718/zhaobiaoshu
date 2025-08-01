#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量文档处理模块

功能说明：
- 支持多个文档文件的批量上传和处理
- 将多个文档的内容合并后生成一份完整的招标书
- 提供文档内容合并、去重和优化功能
- 支持异步处理和进度跟踪
"""

import os
import asyncio
import concurrent.futures
from typing import List, Dict, Any, Optional
from .parser import parse_document_text
from .chunker import chunk_text
from .performance_optimizer import optimize_document_processing, content_cache
from ..llm_service.model_manager import model_manager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.multi_file_settings import multi_file_config


def get_llm_response(prompt: str) -> Optional[str]:
    """获取大模型响应"""
    try:
        response = model_manager.call_model('tender_generation', prompt)
        return response
    except Exception as e:
        print(f"调用大模型时出错: {e}")
        return None


def parse_multiple_documents(file_paths: List[str]) -> Dict[str, str]:
    """解析多个文档并返回文档内容字典
    
    Args:
        file_paths: 文档文件路径列表
        
    Returns:
        Dict[str, str]: 文件名到文档内容的映射
    """
    document_contents = {}
    min_content_length = multi_file_config.get_min_content_length()
    continue_on_error = multi_file_config.should_continue_on_parse_error()
    
    for file_path in file_paths:
        try:
            filename = os.path.basename(file_path)
            print(f"正在解析文档: {filename}")
            
            # 验证文件格式
            if not multi_file_config.validate_file_format(filename):
                print(f"警告: 文件 {filename} 格式不受支持，跳过处理")
                if not continue_on_error:
                    raise ValueError(f"不支持的文件格式: {filename}")
                continue
            
            content = parse_document_text(file_path)
            if content and content.strip() and len(content.strip()) >= min_content_length:
                document_contents[filename] = content
            else:
                print(f"警告: 文档 {filename} 内容为空或过短（少于{min_content_length}字符）")
                if not continue_on_error:
                    raise ValueError(f"文档内容无效: {filename}")
        except Exception as e:
            print(f"解析文档 {file_path} 时出错: {e}")
            if not continue_on_error:
                raise
            continue
    
    return document_contents


def merge_document_contents(document_contents: Dict[str, str]) -> str:
    """合并多个文档的内容
    
    Args:
        document_contents: 文档内容字典
        
    Returns:
        str: 合并后的文档内容
    """
    if not document_contents:
        raise ValueError("没有有效的文档内容可以合并")
    
    # 应用性能优化
    print("正在优化文档内容...")
    optimized_contents = optimize_document_processing(document_contents)
    
    merged_content = ""
    file_names = list(optimized_contents.keys())
    
    # 添加合并说明
    merged_content += f"# 合并文档内容\n\n"
    merged_content += f"本内容由以下 {len(file_names)} 个文档合并而成：\n"
    for i, filename in enumerate(file_names, 1):
        merged_content += f"{i}. {filename}\n"
    merged_content += "\n" + "="*50 + "\n\n"
    
    # 合并各文档内容
    for filename, content in optimized_contents.items():
        merged_content += f"## 文档：{filename}\n\n"
        merged_content += content
        merged_content += "\n\n" + "-"*30 + "\n\n"
    
    return merged_content


def summarize_chunk(chunk: str) -> Optional[str]:
    """对单个文本块进行总结 (Map 步骤)"""
    prompt = f"""请你作为一个专业的招标项目经理，详细总结以下内容的核心要点、关键需求和技术指标。
请确保总结内容清晰、准确，抓住重点。内容如下：

---
{chunk}
---"""
    return get_llm_response(prompt)


def reduce_summaries(summaries: List[str]) -> str:
    """将所有块总结合并成一个最终的全局概述 (Reduce 步骤)"""
    # 过滤掉None值和空字符串
    valid_summaries = [summary for summary in summaries if summary is not None and summary.strip()]
    
    if not valid_summaries:
        print("警告: 所有文本块总结都失败了，无法生成全局概述")
        return "由于模型调用失败，无法生成有效的项目需求概述。请检查模型服务状态。"
    
    combined_summary = "\n\n---\n\n".join(valid_summaries)
    prompt = f"""你是一位顶级的项目需求分析专家。请基于以下多个分散的要点总结，整合并提炼成一份对整个项目全面、连贯、高度概括的需求陈述。
这份陈述将作为后续撰写招标书的唯一依据，因此必须全面、准确、逻辑清晰。

注意：这些总结来自多个不同的文档，请综合考虑所有信息，形成统一的项目需求描述。

总结要点如下：

---
{combined_summary}
---"""
    return get_llm_response(prompt)


def generate_tender_section(overall_summary: str, section_title: str) -> Optional[str]:
    """根据全局概述生成招标书的单个章节"""
    prompt = f"""你是一位资深的标书撰写专家。请根据以下项目的总体需求概述，撰写招标书的'{section_title}'部分。
内容要求专业、详细、符合标准格式，语言严谨。

注意：这个项目需求概述是基于多个文档综合分析得出的，请确保生成的章节内容全面覆盖所有相关要求。

项目总体需求概述：
---
{overall_summary}
---

请开始撰写'{section_title}'的内容："""
    return get_llm_response(prompt)


def process_multiple_documents(file_paths: List[str], config: Optional[Dict[str, Any]] = None) -> str:
    """处理多个文档并生成一份完整的招标书
    
    Args:
        file_paths: 文档文件路径列表
        config: 配置参数
        
    Returns:
        str: 生成的招标书内容
    """
    if not file_paths:
        raise ValueError("文件路径列表不能为空")
    
    config = config or {}
    
    print(f"1. 开始解析 {len(file_paths)} 个文档...")
    document_contents = parse_multiple_documents(file_paths)
    
    if not document_contents:
        raise ValueError("没有成功解析任何文档内容")
    
    print(f"2. 成功解析 {len(document_contents)} 个文档，开始合并内容...")
    merged_content = merge_document_contents(document_contents)
    
    print("3. 开始文本分块...")
    chunks = chunk_text(merged_content)
    
    print(f"4. 开始对 {len(chunks)} 个文本块进行并行总结 (Map)...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        chunk_summaries = list(executor.map(summarize_chunk, chunks))
    
    print("5. 开始整合所有总结 (Reduce)...")
    overall_summary = reduce_summaries(chunk_summaries)
    
    print("6. 开始迭代生成招标书...")
    tender_sections = [
        "第一章 采购公告",
        "第二章 供应商须知",
        "第三章 评审办法",
        "第四章 合同条款及格式",
        "第五章 采购人要求",
        "第六章 响应文件格式"
    ]
    
    # 如果配置中指定了特定章节，则只生成指定章节
    if config.get('include_sections'):
        tender_sections = [section for section in tender_sections if section in config['include_sections']]
    
    # 生成文档标题
    file_names = list(document_contents.keys())
    file_list = "、".join(file_names)
    final_document = f"# 招标书\n\n(基于多文档合并生成 - 源文件: {file_list})\n\n"
    
    # 如果有自定义要求，添加到文档开头
    if config.get('custom_requirements'):
        final_document += f"## 特殊要求\n\n{config['custom_requirements']}\n\n---\n\n"
    
    # 生成各章节内容
    for section_title in tender_sections:
        print(f"   - 正在生成: {section_title}")
        section_content = generate_tender_section(overall_summary, section_title)
        if section_content:
            final_document += f"## {section_title}\n\n{section_content}\n\n---\n\n"
        else:
            final_document += f"## {section_title}\n\n[生成失败，请重试]\n\n---\n\n"
    
    print("7. 多文档招标文件生成完毕！")
    return final_document


async def process_multiple_documents_async(file_paths: List[str], config: Optional[Dict[str, Any]] = None, 
                                         progress_callback=None) -> str:
    """异步处理多个文档并生成招标书
    
    Args:
        file_paths: 文档文件路径列表
        config: 配置参数
        progress_callback: 进度回调函数
        
    Returns:
        str: 生成的招标书内容
    """
    def update_progress(step: int, total_steps: int, message: str):
        if progress_callback:
            progress = int((step / total_steps) * 100)
            progress_callback(progress, message)
    
    total_steps = 7
    
    try:
        update_progress(1, total_steps, f"开始解析 {len(file_paths)} 个文档...")
        document_contents = await asyncio.get_event_loop().run_in_executor(
            None, parse_multiple_documents, file_paths
        )
        
        if not document_contents:
            raise ValueError("没有成功解析任何文档内容")
        
        update_progress(2, total_steps, f"成功解析 {len(document_contents)} 个文档，开始合并内容...")
        merged_content = await asyncio.get_event_loop().run_in_executor(
            None, merge_document_contents, document_contents
        )
        
        update_progress(3, total_steps, "开始文本分块...")
        chunks = await asyncio.get_event_loop().run_in_executor(
            None, chunk_text, merged_content
        )
        
        update_progress(4, total_steps, f"开始对 {len(chunks)} 个文本块进行并行总结...")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            chunk_summaries = await asyncio.get_event_loop().run_in_executor(
                None, lambda: list(executor.map(summarize_chunk, chunks))
            )
        
        update_progress(5, total_steps, "开始整合所有总结...")
        overall_summary = await asyncio.get_event_loop().run_in_executor(
            None, reduce_summaries, chunk_summaries
        )
        
        update_progress(6, total_steps, "开始生成招标书章节...")
        
        config = config or {}
        tender_sections = [
            "第一章 采购公告",
            "第二章 供应商须知",
            "第三章 评审办法",
            "第四章 合同条款及格式",
            "第五章 采购人要求",
            "第六章 响应文件格式"
        ]
        
        if config.get('include_sections'):
            tender_sections = [section for section in tender_sections if section in config['include_sections']]
        
        # 生成文档标题
        file_names = list(document_contents.keys())
        file_list = "、".join(file_names)
        final_document = f"# 招标书\n\n(基于多文档合并生成 - 源文件: {file_list})\n\n"
        
        if config.get('custom_requirements'):
            final_document += f"## 特殊要求\n\n{config['custom_requirements']}\n\n---\n\n"
        
        # 异步生成各章节内容
        for i, section_title in enumerate(tender_sections):
            section_content = await asyncio.get_event_loop().run_in_executor(
                None, generate_tender_section, overall_summary, section_title
            )
            if section_content:
                final_document += f"## {section_title}\n\n{section_content}\n\n---\n\n"
            else:
                final_document += f"## {section_title}\n\n[生成失败，请重试]\n\n---\n\n"
            
            # 更新章节生成进度
            section_progress = 6 + (i + 1) / len(tender_sections)
            update_progress(int(section_progress), total_steps, f"已生成: {section_title}")
        
        update_progress(7, total_steps, "多文档招标文件生成完毕！")
        return final_document
        
    except Exception as e:
        if progress_callback:
            progress_callback(-1, f"处理失败: {str(e)}")
        raise