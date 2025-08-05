# 新建 src/gender_book/enhanced_attachment_processor.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.parser import DocumentParser, get_document_service
import re
from typing import Dict, List, Any, Union
from PIL import Image
import io
import tempfile
import aiofiles
import logging
from fastapi import UploadFile

logger = logging.getLogger(__name__)

class EnhancedAttachmentProcessor:
    def __init__(self):
        # 使用项目现有的Parser技术
        self.document_service = get_document_service()
        self.document_parser = DocumentParser()
        
        # 增强的正则模式库
        self.enhanced_patterns = {
            "营业执照": {
                "keywords": ["营业执照", "Business License", "统一社会信用代码", "Credit Code"],
                "critical_fields": [
                    (r"(?:企业名称|公司名称|Company Name)[：:\s]*([^\n\r]+)", "企业名称"),
                    (r"(?:统一社会信用代码|Credit Code)[：:\s]*([A-Z0-9]{18})", "信用代码"),
                    (r"(?:注册资本|Registered Capital)[：:\s]*([^\n\r]+)", "注册资本"),
                    (r"(?:成立日期|Establishment Date)[：:\s]*(\d{4}[年-]\d{1,2}[月-]\d{1,2})", "成立日期"),
                    (r"(?:营业期限|Business Term)[：:\s]*([^\n\r]+)", "营业期限"),
                    (r"(?:法定代表人|Legal Representative)[：:\s]*([^\n\r]+)", "法定代表人")
                ],
                "validation_rules": [
                    (r"[A-Z0-9]{18}", "信用代码格式检查"),
                    (r"\d{4}[年-]\d{1,2}[月-]\d{1,2}", "日期格式检查")
                ]
            },
            "建筑资质证书": {
                "keywords": ["建筑业企业资质", "Construction Qualification", "资质证书"],
                "critical_fields": [
                    (r"(?:证书编号|Certificate No)[：:\s]*([^\n\r]+)", "证书编号"),
                    (r"(?:资质等级|Qualification Level)[：:\s]*([^\n\r]+)", "资质等级"),
                    (r"(?:资质类别|Qualification Type)[：:\s]*([^\n\r]+)", "资质类别"),
                    (r"(?:有效期至|Valid Until)[：:\s]*(\d{4}[年-]\d{1,2}[月-]\d{1,2})", "有效期"),
                    (r"(?:发证机关|Issuing Authority)[：:\s]*([^\n\r]+)", "发证机关")
                ]
            },
            "安全生产许可证": {
                "keywords": ["安全生产许可证", "Safety Production License"],
                "critical_fields": [
                    (r"(?:许可证编号|License No)[：:\s]*([^\n\r]+)", "许可证编号"),
                    (r"(?:有效期至|Valid Until)[：:\s]*(\d{4}[年-]\d{1,2}[月-]\d{1,2})", "有效期"),
                    (r"(?:发证机关|Issuing Authority)[：:\s]*([^\n\r]+)", "发证机关")
                ]
            },
            "财务报表": {
                "keywords": ["资产负债表", "Balance Sheet", "利润表", "Income Statement"],
                "critical_fields": [
                    (r"(?:总资产|Total Assets)[：:\s]*([0-9,，.]+)", "总资产"),
                    (r"(?:净资产|Net Assets)[：:\s]*([0-9,，.]+)", "净资产"),
                    (r"(?:营业收入|Revenue)[：:\s]*([0-9,，.]+)", "营业收入"),
                    (r"(?:净利润|Net Profit)[：:\s]*([0-9,，.]+)", "净利润"),
                    (r"(\d{4})年度", "报表年度")
                ]
            },
            "法人授权书": {
                "keywords": ["法人授权", "Legal Authorization", "授权委托书", "Power of Attorney"],
                "critical_fields": [
                    (r"(?:法定代表人|Legal Representative)[：:\s]*([^\n\r]+)", "法定代表人"),
                    (r"(?:被授权人|Authorized Person)[：:\s]*([^\n\r]+)", "被授权人"),
                    (r"(?:授权范围|Authorization Scope)[：:\s]*([^\n\r]+)", "授权范围"),
                    (r"(?:有效期|Valid Period)[：:\s]*([^\n\r]+)", "有效期")
                ]
            }
        }
    
    async def process_attachment_with_parser(self, file_path: str, filename: str) -> Dict[str, Any]:
        """使用Parser模块进行高质量文档处理"""
        try:
            # 1. 使用Parser模块解析文档（支持图像OCR）
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # 调用Parser服务进行结构化解析
            parse_result = self.document_service.parse_uploaded_file(
                file_content, 
                filename
            )
            
            if not parse_result['success']:
                raise Exception(f"文档解析失败: {parse_result.get('error', '未知错误')}")
            
            # 2. 提取文本内容
            elements = parse_result['data']['elements']
            extracted_text = self._extract_text_from_elements(elements)
            
            # 3. 智能文档分类
            doc_type = self._classify_document_with_confidence(extracted_text)
            
            # 4. 使用增强正则提取关键信息
            key_info = self._extract_enhanced_key_info(extracted_text, doc_type)
            
            # 5. 验证关键信息完整性
            validation_result = self._validate_extracted_info(key_info, doc_type)
            
            # 6. 处理原始图像数据（如果是图像文件）
            image_data = None
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                # 在文件被删除前读取图像数据
                image_data = file_content  # 直接使用已读取的文件内容
            
            # 构建返回结果
            result = {
                "filename": filename,
                "file_path": file_path,
                "type": "document",
                "document_type": doc_type["type"],
                "confidence": doc_type["confidence"],
                "extracted_text": extracted_text,
                "key_info": key_info,
                "validation": validation_result,
                "original_image_data": image_data,
                "structured_elements": elements,
                "processing_method": "unstructured_parser_hi_res"
            }
            
            # 清理临时文件
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"使用Parser处理文档失败 {filename}: {str(e)}")
            # 确保在异常情况下也清理临时文件
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as cleanup_e:
                logger.warning(f"异常清理临时文件失败: {str(cleanup_e)}")
            raise
    
    async def process_files(self, files: List[UploadFile]) -> Dict[str, Any]:
        """处理上传的附件文件列表"""
        processed_attachments = {
            "files": [],
            "summary": "",
            "key_info": {}
        }
        
        for file in files:
            if not file.filename:
                continue
                
            try:
                # 文件大小限制检查 (10MB)
                file_size = 0
                content = await file.read()
                file_size = len(content)
                
                if file_size > 10 * 1024 * 1024:  # 10MB限制
                    logger.warning(f"文件 {file.filename} 超过大小限制: {file_size} bytes")
                    processed_attachments["files"].append({
                        "filename": file.filename,
                        "error": "文件大小超过10MB限制",
                        "processing_failed": True
                    })
                    continue
                
                # 文件类型验证
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in allowed_extensions:
                    logger.warning(f"不支持的文件类型: {file.filename}")
                    processed_attachments["files"].append({
                        "filename": file.filename,
                        "error": f"不支持的文件类型: {file_ext}",
                        "processing_failed": True
                    })
                    continue
                
                # 保存临时文件
                file_path = await self._save_uploaded_file_content(content, file.filename)
                
                # 处理文件
                result = await self.process_attachment_with_parser(file_path, file.filename)
                processed_attachments["files"].append(result)
                
                # 收集关键信息
                if result.get("key_info"):
                    processed_attachments["key_info"].update(result["key_info"])
                    
            except Exception as e:
                logger.error(f"处理附件 {file.filename} 失败: {str(e)}")
                # 添加失败记录
                processed_attachments["files"].append({
                    "filename": file.filename,
                    "error": str(e),
                    "processing_failed": True
                })
        
        # 生成附件摘要
        processed_attachments["summary"] = self._generate_attachment_summary(
            processed_attachments["files"]
        )
        
        return processed_attachments
    
    async def _save_uploaded_file_content(self, content: bytes, filename: str) -> str:
        """保存上传的文件内容到临时目录"""
        # 创建临时文件
        suffix = os.path.splitext(filename)[1] if filename else '.tmp'
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)
        
        try:
            # 写入文件内容
            with os.fdopen(temp_fd, 'wb') as tmp_file:
                tmp_file.write(content)
            
            return temp_path
        except Exception:
            # 如果出错，清理临时文件
            try:
                os.unlink(temp_path)
            except:
                pass
            raise
    
    def _generate_attachment_summary(self, files_info: List[Dict[str, Any]]) -> str:
        """生成附件摘要"""
        if not files_info:
            return "未上传附件"
        
        summary_parts = []
        success_count = 0
        
        for file_info in files_info:
            if file_info.get("processing_failed"):
                summary_parts.append(f"• {file_info['filename']} (处理失败)")
            else:
                doc_type = file_info.get('document_type', '未知类型')
                confidence = file_info.get('confidence', 0.0)
                summary_parts.append(f"• {file_info['filename']} ({doc_type}, 识别度: {confidence:.1%})")
                success_count += 1
        
        summary = f"共上传 {len(files_info)} 个附件，成功处理 {success_count} 个：\n"
        summary += "\n".join(summary_parts)
        
        return summary
    
    def _extract_text_from_elements(self, elements: List[Dict]) -> str:
        """从解析元素中提取文本"""
        text_parts = []
        for element in elements:
            if element.get('text'):
                text_parts.append(element['text'])
        return '\n'.join(text_parts)
    
    def _classify_document_with_confidence(self, text: str) -> Dict[str, Any]:
        """智能文档分类（带置信度）"""
        max_confidence = 0
        best_type = "其他文件"
        keyword_matches = {}
        
        for doc_type, config in self.enhanced_patterns.items():
            # 计算关键词匹配度
            keywords = config["keywords"]
            matches = sum(1 for keyword in keywords if keyword in text)
            match_ratio = matches / len(keywords)
            
            # 检查关键字段匹配
            field_matches = 0
            for pattern, field_name in config["critical_fields"]:
                if re.search(pattern, text, re.IGNORECASE):
                    field_matches += 1
            
            field_ratio = field_matches / len(config["critical_fields"])
            
            # 综合置信度 = 关键词匹配度 * 0.4 + 字段匹配度 * 0.6
            confidence = match_ratio * 0.4 + field_ratio * 0.6
            
            keyword_matches[doc_type] = {
                "keyword_matches": matches,
                "field_matches": field_matches,
                "confidence": confidence
            }
            
            if confidence > max_confidence:
                max_confidence = confidence
                best_type = doc_type
        
        return {
            "type": best_type,
            "confidence": max_confidence,
            "analysis": keyword_matches
        }
    
    def _extract_enhanced_key_info(self, text: str, doc_classification: Dict) -> Dict[str, str]:
        """使用增强正则提取关键信息"""
        key_info = {}
        doc_type = doc_classification["type"]
        
        if doc_type in self.enhanced_patterns:
            patterns = self.enhanced_patterns[doc_type]["critical_fields"]
            
            for pattern, field_name in patterns:
                # 多次尝试匹配，提高成功率
                matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
                if matches:
                    # 取最长的匹配结果（通常最完整）
                    best_match = max(matches, key=len) if isinstance(matches[0], str) else matches[0]
                    key_info[field_name] = self._clean_extracted_value(best_match)
        
        return key_info
    
    def _clean_extracted_value(self, value: str) -> str:
        """清理提取的值"""
        if not value:
            return ""
        
        # 去除多余空白
        cleaned = re.sub(r'\s+', ' ', value).strip()
        # 去除常见的分隔符
        cleaned = re.sub(r'^[：:\-\s]+|[：:\-\s]+$', '', cleaned)
        
        return cleaned
    
    def _validate_extracted_info(self, key_info: Dict[str, str], doc_type: str) -> Dict[str, Any]:
        """验证提取信息的完整性和正确性"""
        validation = {
            "is_complete": False,
            "missing_fields": [],
            "invalid_fields": [],
            "confidence_score": 0.0
        }
        
        if doc_type in self.enhanced_patterns:
            required_fields = [field[1] for field in self.enhanced_patterns[doc_type]["critical_fields"]]
            
            # 检查完整性
            found_fields = len([f for f in required_fields if f in key_info and key_info[f]])
            completeness = found_fields / len(required_fields)
            
            validation["missing_fields"] = [f for f in required_fields if f not in key_info or not key_info[f]]
            validation["is_complete"] = completeness >= 0.7  # 70%以上认为完整
            validation["confidence_score"] = completeness
            
            # 格式验证（如果有验证规则）
            if "validation_rules" in self.enhanced_patterns[doc_type]:
                for pattern, rule_name in self.enhanced_patterns[doc_type]["validation_rules"]:
                    # 验证逻辑可以进一步扩展
                    pass
        
        return validation

# 集成到投标书生成流程
def _generate_attachments_section_with_enhanced_parser(
    self, attachments_info: Dict[str, Any]
) -> str:
    """基于Parser+正则的高质量附件章节生成"""
    
    prompt = f"""
作为专业的投标文件撰写专家，请根据以下经过高精度OCR和智能解析的附件信息，生成投标书的附件说明章节：

=== 附件清单与详细信息 ===
"""
    
    for file_info in attachments_info['files']:
        confidence = file_info.get('confidence', 0.0)
        validation = file_info.get('validation', {})
        
        prompt += f"""
【文件】：{file_info['filename']}
【文档类型】：{file_info['document_type']}（识别置信度：{confidence:.1%}）
【关键信息】：
"""
        
        key_info = file_info.get('key_info', {})
        for field, value in key_info.items():
            prompt += f"  • {field}：{value}\n"
        
        if validation.get('is_complete'):
            prompt += f"【信息完整性】：✓ 关键信息齐全（完整度：{validation.get('confidence_score', 0):.1%}）\n"
        else:
            missing = validation.get('missing_fields', [])
            prompt += f"【信息完整性】：⚠ 缺少：{', '.join(missing)}\n"
        
        prompt += "\n"
    
    prompt += """
=== 生成要求 ===
1. 基于实际解析的证件信息，生成专业的附件说明
2. 突出关键证件的有效性、合规性和权威性
3. 对于高置信度识别的信息，体现其准确性
4. 对于图像格式证件，说明"附件为高清扫描件，OCR识别准确"
5. 针对识别不完整的信息，说明"详细信息见原件扫描图"
6. 体现企业资质的完整性和投标资格的充分性
7. 字数控制在400-600字，格式专业规范

请生成专业的附件说明内容：
"""
    
    return self.llm_service.model_manager.call_model('tender_notice', prompt)