import time

import time

def optimize_tender_content_for_llm(filtered_data):
    """
    优化过滤后的招标文件，使其更适合大模型理解
    """
    
    def merge_related_fragments(content_list):
        """合并相关的文本片段"""
        merged_content = []
        current_section = ""
        buffer = []
        
        for item in content_list:
            text = item.get("text", "").strip()
            item_type = item.get("type", "")
            
            # 跳过无意义的内容
            if (text in ["*", ":", "**", "***"] or 
                text.startswith("*") and len(text) <= 3 or
                len(text) <= 1):
                continue
            
            # 处理标题
            if item_type == "Title":
                # 如果buffer中有内容，先处理buffer
                if buffer:
                    merged_text = " ".join(buffer).strip()
                    if merged_text and len(merged_text) > 3:
                        merged_content.append({
                            "type": "Content",
                            "text": merged_text,
                            "section": current_section
                        })
                    buffer = []
                
                # 处理标题
                if text.startswith("#"):
                    current_section = text
                    merged_content.append({
                        "type": "Title", 
                        "text": text,
                        "section": current_section
                    })
                elif text.endswith(":") or "：" in text:
                    # 这可能是一个字段标签，加入buffer等待后续内容
                    buffer.append(text)
                else:
                    buffer.append(text)
            
            # 处理其他内容
            elif item_type in ["UncategorizedText", "ListItem"]:
                buffer.append(text)
        
        # 处理最后的buffer
        if buffer:
            merged_text = " ".join(buffer).strip()
            if merged_text and len(merged_text) > 3:
                merged_content.append({
                    "type": "Content",
                    "text": merged_text,
                    "section": current_section
                })
        
        return merged_content
    
    def clean_and_merge_text(content_list):
        """清理并智能合并文本"""
        cleaned_content = []
        
        for i, item in enumerate(content_list):
            text = item["text"]
            
            # 特殊处理：合并被分割的信息
            if (text.endswith("(027") and 
                i + 1 < len(content_list) and 
                content_list[i + 1]["text"].startswith(("8", "1"))):
                # 合并电话号码
                next_text = content_list[i + 1]["text"]
                merged_text = text + next_text
                cleaned_content.append({
                    **item,
                    "text": merged_text
                })
                # 跳过下一个项目（因为已经合并了）
                content_list[i + 1]["skip"] = True
                continue
            
            # 跳过标记为跳过的项目
            if item.get("skip"):
                continue
            
            # 合并数字信息（如"长度6" + "12米"）
            if (text.endswith(("长度", "高度")) and text[-1].isdigit() and
                i + 1 < len(content_list)):
                next_text = content_list[i + 1]["text"]
                if next_text.endswith("米"):
                    merged_text = text + next_text
                    cleaned_content.append({
                        **item,
                        "text": merged_text
                    })
                    content_list[i + 1]["skip"] = True
                    continue
            
            cleaned_content.append(item)
        
        return cleaned_content
    
    # 执行优化
    content = filtered_data.get("content", [])
    
    # 第一步：清理和智能合并
    cleaned_content = clean_and_merge_text(content)
    
    # 第二步：按章节合并相关片段
    merged_content = merge_related_fragments(cleaned_content)
    
    return {"content": merged_content}


def convert_to_structured_text(optimized_data):
    """
    将优化后的数据转换为结构化文本，更适合大模型理解
    """
    
    sections = {}
    current_chapter = ""
    
    for item in optimized_data.get("content", []):
        text = item["text"]
        item_type = item["type"]
        section = item.get("section", "")
        
        if item_type == "Title" and text.startswith("#"):
            current_chapter = text
            if current_chapter not in sections:
                sections[current_chapter] = []
        else:
            if current_chapter:
                sections[current_chapter].append(text)
    
    # 构建结构化文本
    structured_text = []
    
    for chapter, contents in sections.items():
        structured_text.append(f"\n{chapter}\n")
        structured_text.append("-" * 50)
        
        for content in contents:
            if content.strip():
                structured_text.append(content)
        
        structured_text.append("")  # 空行分隔
    
    return "\n".join(structured_text)


def create_llm_friendly_prompt(structured_text):
    """
    创建对大模型友好的提示词
    """
    
    prompt = f"""
基于以下招标文件内容，请帮我生成一份完整、规范的招标书。

=== 原始招标文件内容 ===
{structured_text}

=== 任务要求 ===
1. 整理并完善文档结构，确保逻辑清晰
2. 合并被分割的信息（如电话号码、地址等）
3. 补充必要的格式化，使文档专业规范
4. 保持所有重要信息完整性
5. 按照标准招标书格式组织内容

=== 输出格式 ===
请生成一份markdown格式的完整招标书，包含：
- 标准的文档标题和目录结构
- 完整的项目信息和技术要求
- 规范的时间安排和联系方式
- 专业的格式和排版

请开始生成招标书：
"""
    
    return prompt


# 使用示例
def process_tender_document_optimized(json_data):
    """
    完整的招标文档优化处理流程
    """
    start_time = time.time()
    
    # 1. 优化内容结构
    print("步骤1: 优化内容结构...")
    optimized_data = optimize_tender_content_for_llm(json_data)
    
    # 2. 转换为结构化文本
    print("步骤2: 转换为结构化文本...")
    structured_text = convert_to_structured_text(optimized_data)
    
    # 3. 创建LLM提示词
    print("步骤3: 创建LLM提示词...")
    llm_prompt = create_llm_friendly_prompt(structured_text)
    
    end_time = time.time()
    
    # 4. 计算统计信息
    original_content_count = len(json_data.get("content", []))
    optimized_content_count = len(optimized_data.get("content", []))
    processing_time = round(end_time - start_time, 2)
    optimization_ratio = round((1 - optimized_content_count / original_content_count) * 100, 2) if original_content_count > 0 else 0

    statistics = {
        "original_content_count": original_content_count,
        "optimized_content_count": optimized_content_count,
        "structured_text_length": len(structured_text),
        "llm_prompt_length": len(llm_prompt),
        "processing_time_seconds": processing_time,
        "optimization_ratio_percentage": optimization_ratio
    }
    
    # 输出统计信息
    print(f"\n=== 处理结果 ===")
    print(f"原始内容块数量: {statistics['original_content_count']}")
    print(f"优化后内容块数量: {statistics['optimized_content_count']}")
    print(f"处理耗时: {statistics['processing_time_seconds']}s")

    return {
        "optimized_data": optimized_data,
        "structured_text": structured_text,
        "llm_prompt": llm_prompt,
        "statistics": statistics
    }


# 验证处理效果
def validate_content_integrity(original_data, processed_result):
    """
    验证处理后内容的完整性
    """
    
    # 提取关键信息进行对比
    key_info = {
        "项目名称": "武汉市光谷科创中心",
        "招标编号": "WHGKZB-2025-003",
        "建设单位": "武汉光谷建设开发有限公司",
        "预制梁数量": "1,200根",
        "预制板面积": "15,000平方米",
        "联系人": "李建国"
    }
    
    structured_text = processed_result["structured_text"]
    
    missing_info = []
    for key, value in key_info.items():
        if value not in structured_text:
            missing_info.append(f"{key}: {value}")
    
    if missing_info:
        print("⚠️ 以下关键信息可能丢失:")
        for info in missing_info:
            print(f"  - {info}")
    else:
        print("✅ 所有关键信息都已保留")
    
    return len(missing_info) == 0