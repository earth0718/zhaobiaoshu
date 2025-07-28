import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入现有的LLM服务
from src.llm_service import LLMService
from .section_manager import SectionManager, BidSection

logger = logging.getLogger(__name__)

class BidProposalGenerator:
    """投标书生成器
    
    负责根据招标文件分析结果和章节计划，分章节生成完整的投标书
    """
    
    def __init__(self, model_name: str = None):
        self.logger = logging.getLogger(__name__)
        self.section_manager = SectionManager()
        
        # 初始化LLM服务
        try:
            self.llm_service = LLMService(model_name=model_name)
            self.logger.info(f"LLM服务初始化成功，使用模型: {model_name or '默认模型'}")
        except Exception as e:
            self.logger.error(f"LLM服务初始化失败: {str(e)}")
            raise
    
    def generate_bid_proposal(self, tender_document_json: Dict[str, Any], 
                               model_name: str = None,
                               batch_size: int = None) -> Dict[str, Any]:
        """生成完整的投标书文档
        
        Args:
            tender_document_json: 招标文件JSON数据
            model_name: 指定使用的模型名称
            batch_size: 批处理大小，控制每次生成的章节数量
            
        Returns:
            生成结果，包含完整投标书和生成统计信息
        """
        try:
            self.logger.info("开始生成投标书文档")
            start_time = datetime.now()
            
            # 1. 分析招标文件内容
            self.logger.info("步骤1: 分析招标文件内容")
            content_analysis = self.section_manager.analyze_json_content(tender_document_json)
            
            # 2. 生成投标书章节计划
            self.logger.info("步骤2: 生成投标书章节计划")
            section_plan = self.section_manager.generate_section_plan(content_analysis)
            
            # 3. 生成项目理解（作为全局上下文）
            self.logger.info("步骤3: 生成项目理解")
            project_understanding = self._generate_project_understanding(content_analysis)
            
            # 4. 分批生成投标书章节内容
            self.logger.info("步骤4: 分批生成投标书章节内容")
            batch_size = batch_size or section_plan.get("recommended_batch_size", 3)
            sections_content = self._generate_bid_sections_in_batches(
                section_plan, content_analysis, project_understanding, batch_size
            )
            
            # 5. 组装最终投标书文档
            self.logger.info("步骤5: 组装最终投标书文档")
            final_document = self._assemble_final_bid_document(
                project_understanding, sections_content, content_analysis
            )
            
            # 6. 生成统计信息
            end_time = datetime.now()
            processing_duration = (end_time - start_time).total_seconds()
            
            statistics = {
                "processing_duration": processing_duration,
                "total_sections": len(sections_content),
                "document_length": len(final_document),
                "batch_size_used": batch_size,
                "model_used": model_name or "默认模型",
                "generation_time": end_time.isoformat(),
                "content_analysis_summary": {
                    "total_content_blocks": content_analysis.get("total_content_blocks", 0),
                    "sections_with_requirements": len([s for s in section_plan["sections"] if s["has_requirements"]]),
                    "tender_requirements_extracted": len(content_analysis.get("tender_requirements", {}))
                }
            }
            
            self.logger.info(f"投标书生成完成，耗时: {processing_duration:.2f}秒")
            
            return {
                "success": True,
                "bid_proposal": final_document,
                "statistics": statistics,
                "section_plan": section_plan,
                "content_analysis": content_analysis
            }
            
        except Exception as e:
            self.logger.error(f"生成投标书时出错: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "bid_proposal": "",
                "statistics": {}
            }
    
    def _generate_project_understanding(self, content_analysis: Dict[str, Any]) -> str:
        """生成项目理解，作为后续投标书章节生成的全局上下文"""
        try:
            tender_requirements = content_analysis.get("tender_requirements", {})
            section_mapping = content_analysis.get("section_mapping", {})
            
            # 收集项目理解相关的内容
            understanding_content = section_mapping.get("project_understanding", [])
            
            # 构建项目理解生成提示
            prompt = self._build_understanding_prompt(tender_requirements, understanding_content)
            
            # 调用LLM生成项目理解
            understanding = self.llm_service.model_manager.call_model('tender_notice', prompt)
            
            self.logger.info("项目理解生成完成")
            return understanding
            
        except Exception as e:
            self.logger.error(f"生成项目理解时出错: {str(e)}")
            return "项目理解生成失败"
    
    def _build_understanding_prompt(self, tender_requirements: Dict[str, Any], 
                             understanding_content: List[Dict[str, Any]]) -> str:
        """构建项目理解生成提示"""
        prompt = """你是一位专业的投标文件撰写专家。请根据以下招标文件信息生成一个完整的项目理解，这个理解将作为整个投标书的基础。

=== 招标文件关键信息 ===\n"""
        
        # 添加招标要求信息
        for key, value in tender_requirements.items():
            key_name_map = {
                "project_name": "项目名称",
                "tender_number": "招标编号", 
                "tenderer": "招标人",
                "budget": "项目预算",
                "qualification_requirements": "资格要求",
                "technical_requirements": "技术要求",
                "commercial_conditions": "商务条件",
                "evaluation_criteria": "评标标准",
                "timeline": "时间安排"
            }
            prompt += f"{key_name_map.get(key, key)}: {value}\n"
        
        # 添加相关内容
        if understanding_content:
            prompt += "\n=== 招标文件相关内容 ===\n"
            for item in understanding_content[:10]:  # 限制内容数量
                prompt += f"- {item.get('text', '')}\n"
        
        prompt += """
=== 生成要求 ===
1. 生成一个完整的项目理解，体现对招标需求的深入理解
2. 内容要专业、准确、符合投标文件规范
3. 字数控制在500-800字之间
4. 展现对项目背景、目标、技术要求、商务要求的理解
5. 体现投标人的专业能力和项目把握能力
6. 输出格式为纯文本，不需要markdown格式

请开始生成项目理解："""
        
        return prompt
    
    def _generate_bid_sections_in_batches(self, section_plan: Dict[str, Any],
                                    content_analysis: Dict[str, Any],
                                    project_understanding: str,
                                    batch_size: int) -> Dict[str, str]:
        """分批生成投标书章节内容"""
        sections_content = {}
        sections = section_plan["sections"]
        
        # 按批次处理章节
        for i in range(0, len(sections), batch_size):
            batch = sections[i:i + batch_size]
            self.logger.info(f"正在处理第{i//batch_size + 1}批投标书章节，包含{len(batch)}个章节")
            
            # 生成当前批次的章节
            for section in batch:
                section_id = section["id"]
                try:
                    content = self._generate_single_bid_section(
                        section_id, content_analysis, project_understanding, sections_content
                    )
                    sections_content[section_id] = content
                    self.logger.info(f"投标书章节 {section['title']} 生成完成")
                except Exception as e:
                    self.logger.error(f"生成投标书章节 {section['title']} 时出错: {str(e)}")
                    sections_content[section_id] = f"章节生成失败: {str(e)}"
        
        return sections_content
    
    def _generate_single_bid_section(self, section_id: str, 
                               content_analysis: Dict[str, Any],
                               project_understanding: str,
                               existing_sections: Dict[str, str]) -> str:
        """生成单个投标书章节内容"""
        try:
            # 获取章节上下文
            section_context = self.section_manager.get_section_context(section_id, content_analysis)
            
            # 构建投标书章节生成提示
            prompt = self._build_bid_section_prompt(
                section_context, project_understanding, existing_sections
            )
            
            # 调用LLM生成投标书章节内容
            section_content = self.llm_service.model_manager.call_model('tender_notice', prompt)
            
            return section_content
            
        except Exception as e:
            self.logger.error(f"生成投标书章节 {section_id} 时出错: {str(e)}")
            raise
    
    def _build_bid_section_prompt(self, section_context: Dict[str, Any],
                            project_understanding: str,
                            existing_sections: Dict[str, str]) -> str:
        """构建投标书章节生成提示"""
        section_info = section_context["section_info"]
        tender_requirements = section_context["tender_requirements"]
        project_info = section_context["project_info"]
        response_hints = section_context["response_hints"]
        
        prompt = f"""你是一位专业的投标文件撰写专家。请根据以下信息生成投标书的「{section_info['title']}」章节。

=== 项目理解（全局上下文） ===
{project_understanding}

=== 章节要求 ===
章节标题: {section_info['title']}
章节描述: {section_info['description']}
关键词: {', '.join(section_info['keywords'])}
"""
        
        # 添加响应提示
        if response_hints:
            prompt += "\n=== 投标响应提示 ===\n"
            for hint in response_hints:
                prompt += f"- {hint}\n"
        
        # 添加招标文件相关要求
        if tender_requirements:
            prompt += "\n=== 招标文件相关要求 ===\n"
            for item in tender_requirements[:8]:  # 限制内容数量避免超出token限制
                prompt += f"- {item.get('text', '')}\n"
        
        # 添加已生成的相关章节（用于保持一致性）
        related_sections = section_context.get("related_sections", [])
        if related_sections and existing_sections:
            prompt += "\n=== 相关已生成投标书章节（供参考） ===\n"
            for related_id in related_sections:
                if related_id in existing_sections:
                    related_content = existing_sections[related_id][:300]  # 只取前300字符
                    prompt += f"- {related_content}...\n"
        
        prompt += """
=== 生成要求 ===
1. 内容要专业、准确、符合投标文件规范
2. 结构清晰，逻辑合理，充分响应招标要求
3. 字数控制在400-1000字之间
4. 突出投标人的优势和能力，展现专业性
5. 保持与项目理解和其他投标书章节的一致性
6. 如果招标要求不足，可以基于常见的投标项目进行合理补充
7. 输出格式为纯文本，不需要markdown格式
8. 不要重复章节标题，直接输出章节内容

请开始生成投标书章节内容："""
        
        return prompt
    
    def _assemble_final_bid_document(self, project_understanding: str,
                               sections_content: Dict[str, str],
                               content_analysis: Dict[str, Any]) -> str:
        """组装最终的投标书文档"""
        try:
            tender_requirements = content_analysis.get("tender_requirements", {})
            
            # 构建文档头部
            document_title = tender_requirements.get("project_name", "投标项目") + " 投标书"
            
            document_parts = []
            document_parts.append(f"# {document_title}")
            document_parts.append("")
            
            # 添加基本信息
            if tender_requirements:
                document_parts.append("## 基本信息")
                document_parts.append("")
                for key, value in tender_requirements.items():
                    key_name_map = {
                        "project_name": "项目名称",
                        "tender_number": "招标编号",
                        "tenderer": "招标人", 
                        "budget": "项目预算",
                        "timeline": "项目时间",
                        "contact_info": "联系方式"
                    }
                    document_parts.append(f"**{key_name_map.get(key, key)}**: {value}")
                document_parts.append("")
                document_parts.append("---")
                document_parts.append("")
            
            # 添加项目理解
            document_parts.append("## 项目理解")
            document_parts.append("")
            document_parts.append(project_understanding)
            document_parts.append("")
            document_parts.append("---")
            document_parts.append("")
            
            # 按顺序添加各投标书章节
            section_order = [
                "company_overview",
                "qualification_response", 
                "technical_solution",
                "project_management",
                "commercial_proposal",
                "service_commitment",
                "project_understanding",
                "attachments"
            ]
            
            for section_id in section_order:
                if section_id in sections_content:
                    section_template = self.section_manager.standard_sections[section_id]
                    document_parts.append(f"## {section_template.title}")
                    document_parts.append("")
                    document_parts.append(sections_content[section_id])
                    document_parts.append("")
                    document_parts.append("---")
                    document_parts.append("")
            
            # 添加文档尾部
            document_parts.append("## 附录")
            document_parts.append("")
            document_parts.append(f"本投标书由系统自动生成，生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
            document_parts.append("")
            
            final_document = "\n".join(document_parts)
            
            self.logger.info(f"最终投标书文档组装完成，总长度: {len(final_document)} 字符")
            return final_document
            
        except Exception as e:
            self.logger.error(f"组装最终投标书文档时出错: {str(e)}")
            raise
    
    def generate_bid_outline(self, tender_document_json: Dict[str, Any]) -> Dict[str, Any]:
        """仅生成投标书章节大纲，不生成具体内容
        
        用于快速预览将要生成的投标书章节结构
        """
        try:
            self.logger.info("开始生成投标书章节大纲")
            
            # 分析招标文件内容
            content_analysis = self.section_manager.analyze_json_content(tender_document_json)
            
            # 生成投标书章节计划
            section_plan = self.section_manager.generate_section_plan(content_analysis)
            
            # 构建大纲
            outline = {
                "document_title": content_analysis.get("tender_requirements", {}).get("project_name", "投标项目") + " 投标书",
                "total_sections": len(section_plan["sections"]),
                "estimated_total_tokens": section_plan["total_estimated_tokens"],
                "recommended_batch_size": section_plan["recommended_batch_size"],
                "sections": []
            }
            
            for section in section_plan["sections"]:
                outline["sections"].append({
                    "title": section["title"],
                    "description": section["description"],
                    "has_requirements": section["has_requirements"],
                    "requirement_items": section["requirement_items"],
                    "estimated_tokens": section["estimated_tokens"]
                })
            
            self.logger.info("投标书章节大纲生成完成")
            return {
                "success": True,
                "outline": outline,
                "content_analysis_summary": {
                    "total_content_blocks": content_analysis.get("total_content_blocks", 0),
                    "tender_requirements_count": len(content_analysis.get("tender_requirements", {}))
                }
            }
            
        except Exception as e:
            self.logger.error(f"生成投标书章节大纲时出错: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "outline": {}
            }