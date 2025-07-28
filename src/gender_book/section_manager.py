import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class BidSection:
    """投标书章节数据结构"""
    id: str
    title: str
    description: str
    content_keywords: List[str]
    priority: int
    estimated_length: int
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class SectionManager:
    """投标书章节管理器
    
    负责分析招标文件JSON数据，智能生成投标书章节结构
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 预定义的标准投标书章节模板（投标人响应招标文件的结构）
        self.standard_sections = {
            "company_overview": BidSection(
                id="company_overview",
                title="第一章 投标人基本情况",
                description="公司简介、资质证书、组织架构等",
                content_keywords=["公司简介", "注册资本", "成立时间", "经营范围", "资质证书"],
                priority=1,
                estimated_length=1000
            ),
            "qualification_response": BidSection(
                id="qualification_response", 
                title="第二章 资格条件响应",
                description="对招标文件中资格要求的逐项响应",
                content_keywords=["资质要求", "业绩要求", "财务状况", "技术能力", "人员配备"],
                priority=2,
                estimated_length=1200
            ),
            "technical_solution": BidSection(
                id="technical_solution",
                title="第三章 技术方案",
                description="针对招标技术要求的详细技术解决方案",
                content_keywords=["技术方案", "施工方案", "质量保证", "技术创新", "工艺流程"],
                priority=3,
                estimated_length=2000
            ),
            "project_management": BidSection(
                id="project_management",
                title="第四章 项目管理方案",
                description="项目组织架构、进度计划、质量管理等",
                content_keywords=["项目组织", "进度计划", "质量管理", "安全管理", "风险控制"],
                priority=4,
                estimated_length=1500
            ),
            "commercial_proposal": BidSection(
                id="commercial_proposal",
                title="第五章 商务报价",
                description="详细报价清单、付款条件、商务条款响应",
                content_keywords=["报价清单", "付款条件", "履约保证", "质保期", "商务条款"],
                priority=5,
                estimated_length=1000
            ),
            "service_commitment": BidSection(
                id="service_commitment",
                title="第六章 服务承诺",
                description="质量承诺、进度承诺、售后服务等",
                content_keywords=["质量承诺", "进度承诺", "售后服务", "培训服务", "维护保养"],
                priority=6,
                estimated_length=800
            ),
            "project_understanding": BidSection(
                id="project_understanding",
                title="第七章 项目理解",
                description="对招标项目的理解和分析",
                content_keywords=["项目理解", "难点分析", "解决措施", "实施建议"],
                priority=7,
                estimated_length=1000
            ),
            "attachments": BidSection(
                id="attachments",
                title="第八章 附件",
                description="相关证明文件、业绩证明等附件",
                content_keywords=["营业执照", "资质证书", "业绩证明", "财务报表", "授权书"],
                priority=8,
                estimated_length=500
            )
        }
    
    def analyze_json_content(self, filtered_json: Dict[str, Any]) -> Dict[str, Any]:
        """分析招标文件JSON数据，提取关键信息用于生成投标书
        
        Args:
            filtered_json: 招标文件JSON数据
            
        Returns:
            分析结果，包含投标书响应所需的关键信息
        """
        try:
            self.logger.info("开始分析招标文件JSON内容")
            
            content_analysis = {
                "total_content_blocks": 0,
                "tender_requirements": {},  # 招标文件要求
                "bid_response_mapping": {},  # 投标书响应映射
                "key_information": {},
                "section_mapping": {},
                "content_distribution": {}
            }
            
            # 获取内容列表
            content_list = filtered_json.get("content", [])
            content_analysis["total_content_blocks"] = len(content_list)
            
            # 分析招标文件内容，提取投标书需要响应的要求
            for item in content_list:
                text = item.get("text", "")
                section = item.get("section", "")
                item_type = item.get("type", "unknown")
                
                # 提取招标文件中的关键要求信息
                self._extract_tender_requirements(text, content_analysis["tender_requirements"])
                
                # 映射到投标书响应章节
                mapped_bid_sections = self._map_to_bid_sections(text, section)
                for section_id in mapped_bid_sections:
                    if section_id not in content_analysis["section_mapping"]:
                        content_analysis["section_mapping"][section_id] = []
                    content_analysis["section_mapping"][section_id].append({
                        "text": text,
                        "original_section": section,
                        "type": item_type,
                        "requirement_type": self._classify_requirement_type(text)
                    })
            
            # 计算内容分布
            for section_id, items in content_analysis["section_mapping"].items():
                content_analysis["content_distribution"][section_id] = {
                    "item_count": len(items),
                    "total_length": sum(len(item["text"]) for item in items),
                    "avg_length": sum(len(item["text"]) for item in items) / len(items) if items else 0,
                    "requirement_types": list(set(item["requirement_type"] for item in items))
                }
            
            # 生成投标书响应结构
            content_analysis["bid_response_mapping"] = self._generate_bid_response_structure(content_analysis)
            
            self.logger.info(f"招标文件分析完成，共{content_analysis['total_content_blocks']}个内容块，需要响应{len(content_analysis['section_mapping'])}个投标书章节")
            return content_analysis
            
        except Exception as e:
            self.logger.error(f"分析招标文件时出错: {str(e)}")
            raise
    
    def _extract_tender_requirements(self, text: str, requirements: Dict[str, Any]):
        """从招标文件文本中提取关键要求信息"""
        # 项目基本信息
        if "项目名称" in text or "工程名称" in text:
            project_match = re.search(r'项目名称[：:](.*?)(?=[\n，。]|$)', text)
            if project_match:
                requirements["project_name"] = project_match.group(1).strip()
        
        # 招标编号
        if "招标编号" in text or "项目编号" in text:
            number_match = re.search(r'(?:招标|项目)编号[：:]([A-Z0-9\-]+)', text)
            if number_match:
                requirements["tender_number"] = number_match.group(1).strip()
        
        # 招标人/采购人
        if "招标人" in text or "采购人" in text or "建设单位" in text:
            unit_match = re.search(r'(?:招标人|采购人|建设单位)[：:](.*?)(?=[\n，。]|$)', text)
            if unit_match:
                requirements["tenderer"] = unit_match.group(1).strip()
        
        # 预算金额
        if "预算" in text or "投资" in text or "控制价" in text:
            budget_match = re.search(r'(?:预算|投资|控制价)[^0-9]*([0-9,，.]+)(?:万元|元|万)', text)
            if budget_match:
                requirements["budget"] = budget_match.group(1).strip()
        
        # 资格要求
        if "资质要求" in text or "资格条件" in text:
            if "qualification_requirements" not in requirements:
                requirements["qualification_requirements"] = []
            requirements["qualification_requirements"].append(text)
        
        # 技术要求
        if "技术要求" in text or "技术规格" in text or "技术标准" in text:
            if "technical_requirements" not in requirements:
                requirements["technical_requirements"] = []
            requirements["technical_requirements"].append(text)
        
        # 商务要求
        if "商务要求" in text or "合同条款" in text or "付款方式" in text:
            if "commercial_requirements" not in requirements:
                requirements["commercial_requirements"] = []
            requirements["commercial_requirements"].append(text)
        
        # 评标标准
        if "评标" in text or "评分" in text or "评审" in text:
            if "evaluation_criteria" not in requirements:
                requirements["evaluation_criteria"] = []
            requirements["evaluation_criteria"].append(text)
        
        # 时间要求
        if "投标截止" in text or "开标时间" in text or "工期" in text:
            if "timeline_requirements" not in requirements:
                requirements["timeline_requirements"] = []
            requirements["timeline_requirements"].append(text)
    
    def _map_to_bid_sections(self, text: str, original_section: str) -> List[str]:
        """将招标文件内容映射到投标书响应章节"""
        mapped_sections = []
        
        # 基于关键词映射到投标书章节
        for section_id, section in self.standard_sections.items():
            for keyword in section.content_keywords:
                if keyword in text:
                    mapped_sections.append(section_id)
                    break
        
        # 基于招标文件章节名称映射到投标书响应章节
        if original_section:
            if "资格" in original_section or "资质" in original_section:
                mapped_sections.extend(["company_overview", "qualification_response"])
            elif "技术" in original_section or "规格" in original_section or "标准" in original_section:
                mapped_sections.extend(["technical_solution", "project_management"])
            elif "商务" in original_section or "合同" in original_section or "付款" in original_section:
                mapped_sections.append("commercial_proposal")
            elif "评标" in original_section or "评审" in original_section or "评分" in original_section:
                mapped_sections.append("service_commitment")
            elif "项目" in original_section or "概述" in original_section or "背景" in original_section:
                mapped_sections.append("project_understanding")
            elif "投标文件" in original_section or "格式" in original_section:
                mapped_sections.append("attachments")
        
        # 基于文本内容智能映射
        if "资质证书" in text or "营业执照" in text or "公司" in text:
            mapped_sections.append("company_overview")
        if "技术方案" in text or "施工方案" in text or "实施方案" in text:
            mapped_sections.append("technical_solution")
        if "项目管理" in text or "进度计划" in text or "质量管理" in text:
            mapped_sections.append("project_management")
        if "报价" in text or "价格" in text or "费用" in text:
            mapped_sections.append("commercial_proposal")
        if "服务承诺" in text or "质量承诺" in text or "售后" in text:
            mapped_sections.append("service_commitment")
        if "项目理解" in text or "难点" in text or "风险" in text:
            mapped_sections.append("project_understanding")
        
        # 如果没有映射到任何章节，默认归类到项目理解
        if not mapped_sections:
            mapped_sections.append("project_understanding")
        
        return list(set(mapped_sections))  # 去重
    
    def _classify_requirement_type(self, text: str) -> str:
        """分类招标文件要求类型"""
        if "资质" in text or "资格" in text or "证书" in text:
            return "qualification"
        elif "技术" in text or "规格" in text or "标准" in text or "工艺" in text:
            return "technical"
        elif "商务" in text or "价格" in text or "报价" in text or "付款" in text:
            return "commercial"
        elif "评标" in text or "评分" in text or "评审" in text:
            return "evaluation"
        elif "时间" in text or "工期" in text or "进度" in text:
            return "timeline"
        elif "质量" in text or "验收" in text or "标准" in text:
            return "quality"
        elif "服务" in text or "维护" in text or "培训" in text:
            return "service"
        else:
            return "general"
    
    def _generate_bid_response_structure(self, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成投标书响应结构"""
        response_structure = {}
        
        for section_id, section_template in self.standard_sections.items():
            if section_id in content_analysis["section_mapping"]:
                # 有对应招标文件要求的章节
                mapped_content = content_analysis["section_mapping"][section_id]
                response_structure[section_id] = {
                    "title": section_template.title,
                    "description": section_template.description,
                    "priority": section_template.priority,
                    "has_requirements": True,
                    "requirement_count": len(mapped_content),
                    "response_hints": self._generate_response_hints(section_id, mapped_content),
                    "estimated_length": section_template.estimated_length
                }
            else:
                # 没有直接对应要求但需要主动提供的章节
                response_structure[section_id] = {
                    "title": section_template.title,
                    "description": section_template.description,
                    "priority": section_template.priority,
                    "has_requirements": False,
                    "requirement_count": 0,
                    "response_hints": self._generate_default_response_hints(section_id),
                    "estimated_length": section_template.estimated_length
                }
        
        return response_structure
    
    def _generate_response_hints(self, section_id: str, mapped_content: List[Dict]) -> List[str]:
        """根据招标文件要求生成投标书响应提示"""
        hints = []
        
        if section_id == "company_overview":
            hints = [
                "详细介绍公司基本情况、成立时间、注册资本",
                "展示公司资质证书和经营范围",
                "说明公司组织架构和管理团队",
                "突出公司在相关领域的经验和优势"
            ]
        elif section_id == "qualification_response":
            hints = [
                "逐项响应招标文件中的资格要求",
                "提供相应的证明文件和业绩材料",
                "说明如何满足技术和财务要求",
                "展示项目团队的专业能力"
            ]
        elif section_id == "technical_solution":
            hints = [
                "针对招标技术要求提供详细解决方案",
                "说明技术路线和实施方法",
                "突出技术创新点和优势",
                "提供质量保证措施"
            ]
        elif section_id == "project_management":
            hints = [
                "制定详细的项目实施计划",
                "说明项目组织架构和人员配置",
                "提供进度控制和质量管理措施",
                "制定风险控制和应急预案"
            ]
        elif section_id == "commercial_proposal":
            hints = [
                "提供详细的报价清单和计算依据",
                "说明付款条件和商务条款",
                "响应招标文件的商务要求",
                "提供履约保证和质保承诺"
            ]
        elif section_id == "service_commitment":
            hints = [
                "承诺项目质量和进度目标",
                "提供完善的售后服务方案",
                "说明培训和技术支持安排",
                "制定维护保养计划"
            ]
        elif section_id == "project_understanding":
            hints = [
                "深入分析项目特点和难点",
                "说明对招标文件的理解",
                "提出项目实施建议和优化方案",
                "分析潜在风险和解决措施"
            ]
        elif section_id == "attachments":
            hints = [
                "提供营业执照等基础证明文件",
                "附上相关资质证书和业绩证明",
                "包含财务报表和信用证明",
                "提供法人授权书等法律文件"
            ]
        
        return hints
    
    def _generate_default_response_hints(self, section_id: str) -> List[str]:
        """为没有直接招标要求的章节生成默认响应提示"""
        return self._generate_response_hints(section_id, [])
    
    def generate_section_plan(self, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成投标书章节生成计划
        
        Args:
            content_analysis: 招标文件分析结果
            
        Returns:
            投标书章节生成计划
        """
        try:
            self.logger.info("开始生成投标书章节计划")
            
            section_plan = {
                "sections": [],
                "generation_order": [],
                "total_estimated_tokens": 0,
                "recommended_batch_size": 3,  # 建议每批处理的章节数
                "tender_requirements": content_analysis.get("tender_requirements", {}),
                "bid_response_mapping": content_analysis.get("bid_response_mapping", {})
            }
            
            # 根据招标文件要求确定需要生成的投标书章节
            section_mapping = content_analysis.get("section_mapping", {})
            content_distribution = content_analysis.get("content_distribution", {})
            
            for section_id, section_template in self.standard_sections.items():
                if section_id in section_mapping and section_mapping[section_id]:
                    # 有对应招标文件要求的章节
                    section_info = {
                        "id": section_id,
                        "title": section_template.title,
                        "description": section_template.description,
                        "priority": section_template.priority,
                        "has_requirements": True,
                        "requirement_items": len(section_mapping[section_id]),
                        "estimated_tokens": self._estimate_tokens(section_mapping[section_id]),
                        "tender_requirements": section_mapping[section_id][:5],  # 只保留前5个作为示例
                        "response_type": "requirement_based"
                    }
                else:
                    # 没有直接招标要求但需要主动提供的章节
                    section_info = {
                        "id": section_id,
                        "title": section_template.title,
                        "description": section_template.description,
                        "priority": section_template.priority,
                        "has_requirements": False,
                        "requirement_items": 0,
                        "estimated_tokens": section_template.estimated_length,
                        "tender_requirements": [],
                        "response_type": "proactive"
                    }
                
                section_plan["sections"].append(section_info)
                section_plan["total_estimated_tokens"] += section_info["estimated_tokens"]
            
            # 按优先级排序
            section_plan["sections"].sort(key=lambda x: x["priority"])
            section_plan["generation_order"] = [s["id"] for s in section_plan["sections"]]
            
            # 根据token数量调整批处理大小
            avg_tokens_per_section = section_plan["total_estimated_tokens"] / len(section_plan["sections"])
            if avg_tokens_per_section > 1000:
                section_plan["recommended_batch_size"] = 2
            elif avg_tokens_per_section > 1500:
                section_plan["recommended_batch_size"] = 1
            
            self.logger.info(f"投标书章节计划生成完成，共{len(section_plan['sections'])}个章节")
            return section_plan
            
        except Exception as e:
            self.logger.error(f"生成投标书章节计划时出错: {str(e)}")
            raise
    
    def _estimate_tokens(self, content_items: List[Dict[str, Any]]) -> int:
        """估算内容的token数量"""
        total_chars = sum(len(item.get("text", "")) for item in content_items)
        # 中文大约2.5个字符对应1个token
        return int(total_chars / 2.5) + 200  # 加上提示词的token
    
    def get_section_context(self, section_id: str, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """获取特定投标书章节的上下文信息
        
        Args:
            section_id: 章节ID
            content_analysis: 招标文件分析结果
            
        Returns:
            投标书章节上下文信息
        """
        try:
            section_template = self.standard_sections.get(section_id)
            if not section_template:
                raise ValueError(f"未知的章节ID: {section_id}")
            
            section_mapping = content_analysis.get("section_mapping", {})
            tender_requirements = content_analysis.get("tender_requirements", {})
            
            context = {
                "section_info": {
                    "id": section_id,
                    "title": section_template.title,
                    "description": section_template.description,
                    "keywords": section_template.content_keywords
                },
                "tender_requirements": section_mapping.get(section_id, []),
                "project_info": tender_requirements,
                "related_sections": self._get_related_bid_sections(section_id),
                "response_hints": self._get_bid_response_hints(section_id, tender_requirements)
            }
            
            return context
            
        except Exception as e:
            self.logger.error(f"获取投标书章节上下文时出错: {str(e)}")
            raise
    
    def _get_related_bid_sections(self, section_id: str) -> List[str]:
        """获取相关投标书章节
        
        Args:
            section_id: 章节ID
            
        Returns:
            相关投标书章节ID列表
        """
        # 定义投标书章节间的关联关系
        relations = {
            "company_overview": ["qualification_response", "technical_solution"],
            "qualification_response": ["company_overview", "commercial_proposal"],
            "technical_solution": ["company_overview", "project_management"],
            "project_management": ["technical_solution", "service_commitment"],
            "commercial_proposal": ["qualification_response", "service_commitment"],
            "service_commitment": ["commercial_proposal", "project_management"],
            "project_understanding": ["technical_solution", "project_management"],
            "attachments": ["company_overview", "qualification_response"]
        }
        
        return relations.get(section_id, [])
    
    def _get_bid_response_hints(self, section_id: str, key_info: Dict[str, Any]) -> List[str]:
        """获取投标书响应提示"""
        hints = []
        
        if section_id == "company_overview":
            if "project_name" in key_info:
                hints.append(f"针对项目：{key_info['project_name']}")
            if "tenderer" in key_info:
                hints.append(f"招标人：{key_info['tenderer']}")
            hints.append("突出公司在相关领域的经验和优势")
        
        elif section_id == "qualification_response":
            if "qualification_requirements" in key_info:
                hints.append("逐项响应招标文件中的资格要求")
            hints.append("提供相应的证明文件和业绩材料")
        
        elif section_id == "technical_solution":
            if "technical_requirements" in key_info:
                hints.append("针对招标技术要求提供详细解决方案")
            hints.append("突出技术创新点和优势")
        
        elif section_id == "commercial_proposal":
            if "budget" in key_info:
                hints.append(f"参考预算：{key_info['budget']}")
            hints.append("提供详细的报价清单和计算依据")
        
        return hints