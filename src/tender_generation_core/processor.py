#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标文件生成核心处理模块

功能说明：
- 实现招标文件生成的完整流程，包括文档解析、文本分块、内容总结和招标文件章节生成
- 采用Map-Reduce模式对大文档进行并行处理和总结
- 集成统一的模型管理器，支持多种大语言模型调用
- 提供从原始文档到完整招标书的端到端转换能力
"""

import os
import configparser
import concurrent.futures
from .parser import parse_document_text
from .chunker import chunk_text
# 导入统一的模型管理器
from ..llm_service.model_manager import model_manager

# --- 配置 --- #
config = configparser.ConfigParser()
# 修正：确保文件路径正确，并使用 utf-8 编码
config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'tender_generation_config.ini')
try:
    config.read(config_path, encoding='utf-8')
except Exception as e:
    print(f"读取 tender_generation_config.ini 文件失败: {e}")
    # 提供一个默认的回退或直接抛出异常
    raise

# 使用统一的模型管理器
print(f"招标文件生成模块使用模型管理器，当前模型: {model_manager.get_current_model('tender_generation')}")

def get_llm_response(prompt):
    """获取大模型响应"""
    try:
        # 使用统一的模型管理器调用模型
        response = model_manager.call_model('tender_generation', prompt)
        return response
    except Exception as e:
        print(f"调用大模型时出错: {e}")
        return None

def summarize_chunk(chunk):
    """调用 LLM 对单个文本块进行总结 (Map 步骤)"""
    prompt = f"请你作为一个专业的招标项目经理，详细总结以下内容的核心要点、关键需求和技术指标。请确保总结内容清晰、准确，抓住重点。内容如下：\n\n---\n{chunk}\n---"
    return get_llm_response(prompt)

def reduce_summaries(summaries):
    """将所有块总结合并成一个最终的全局概述 (Reduce 步骤)"""
    # 过滤掉None值，避免join操作失败
    valid_summaries = [summary for summary in summaries if summary is not None and summary.strip()]
    
    if not valid_summaries:
        print("警告: 所有文本块总结都失败了，无法生成全局概述")
        return "由于模型调用失败，无法生成有效的项目需求概述。请检查模型服务状态。"
    
    combined_summary = "\n\n---\n\n".join(valid_summaries)
    prompt = f"你是一位顶级的项目需求分析专家。请基于以下多个分散的要点总结，整合并提炼成一份对整个项目全面、连贯、高度概括的需求陈述。这份陈述将作为后续撰写招标书的唯一依据，因此必须全面、准确、逻辑清晰。总结要点如下：\n\n---\n{combined_summary}\n---"
    return get_llm_response(prompt)

def generate_tender_section(overall_summary, section_title):
    """根据全局概述，生成招标书的单个章节 (迭代生成步骤)"""
    prompt = f"""你是一位资深的标书撰写专家。请根据以下项目的总体需求概述，撰写招标书的'{section_title}'部分。内容要求专业、详细、符合标准格式，语言严谨。

项目总体需求概述：
---
{overall_summary}
---

请开始撰写'{section_title}'的内容："""
    return get_llm_response(prompt)

def process_document(filepath):
    """核心处理流程函数"""
    print(f"1. 开始解析文档: {filepath}")
    text = parse_document_text(filepath)
    if not text:
        raise ValueError("无法从文档中提取文本内容")

    print("2. 开始文本分块...")
    chunks = chunk_text(text)
    
    print(f"3. 开始对 {len(chunks)} 个文本块进行并行总结 (Map)...")
    # 保持并行处理
    with concurrent.futures.ThreadPoolExecutor() as executor:
        chunk_summaries = list(executor.map(summarize_chunk, chunks))
    
    print("4. 开始整合所有总结 (Reduce)...")
    overall_summary = reduce_summaries(chunk_summaries)
    
    print("5. 开始迭代生成招标书...")
    tender_sections = [
        "第一章 采购公告",
        "第二章 供应商须知",
        "第三章 评审办法",
        "第四章 合同条款及格式",
        "第五章 采购人要求",
        "第六章 响应文件格式"
    ]
    
    final_document = f"# 招标书\n\n(基于文件 {os.path.basename(filepath)} 生成)\n\n"
    for section_title in tender_sections:
        print(f"   - 正在生成: {section_title}")
        section_content = generate_tender_section(overall_summary, section_title)
        final_document += f"## {section_title}\n\n{section_content}\n\n---\n\n"
        
    print("6. 招标文件生成完毕！")
    return final_document

def process_text_content(text_content, config):
    """处理用户输入的文本内容生成招标书"""
    print("1. 开始处理用户输入的文本内容...")
    
    if not text_content or len(text_content.strip()) < 10:
        raise ValueError("文本内容不能为空且至少需要10个字符")
    
    # 获取项目名称
    project_name = config.get('project_name', '招标项目')
    
    print("2. 开始文本分块...")
    chunks = chunk_text(text_content)
    
    print(f"3. 开始对 {len(chunks)} 个文本块进行并行总结 (Map)...")
    # 保持并行处理
    with concurrent.futures.ThreadPoolExecutor() as executor:
        chunk_summaries = list(executor.map(summarize_chunk, chunks))
    
    print("4. 开始整合所有总结 (Reduce)...")
    overall_summary = reduce_summaries(chunk_summaries)
    
    print("5. 开始迭代生成招标书...")
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
    
    final_document = f"# 招标书\n\n(基于用户输入文本生成 - 项目: {project_name})\n\n"
    
    # 如果有自定义要求，添加到文档开头
    if config.get('custom_requirements'):
        final_document += f"## 特殊要求\n\n{config['custom_requirements']}\n\n---\n\n"
    
    for section_title in tender_sections:
        print(f"   - 正在生成: {section_title}")
        section_content = generate_tender_section(overall_summary, section_title)
        final_document += f"## {section_title}\n\n{section_content}\n\n---\n\n"
        
    print("6. 基于文本的招标文件生成完毕！")
    return final_document