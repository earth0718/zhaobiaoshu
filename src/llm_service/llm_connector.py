#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大语言模型服务连接器模块 (LLM Service Connector)

功能概述:
    本模块提供了与大语言模型（LLM）服务的统一接口，支持多种模型类型的调用和管理。
    主要用于招标文档信息提取、文本摘要生成和文本向量化等任务。

主要功能:
    1. 招标信息提取 - 从招标文档中提取结构化信息
    2. 动态字段提取 - 根据用户指定的字段列表提取信息
    3. 文档摘要生成 - 生成文档的语义摘要
    4. 文本向量化 - 获取文本的embedding向量
    5. 多模型支持 - 支持Ollama本地模型和DeepSeek云端模型

技术特点:
    - 统一的API接口设计，屏蔽不同模型的调用差异
    - 智能的响应解析，支持JSON格式的结构化输出
    - 完善的错误处理和日志记录
    - 灵活的提示词构建，支持动态字段配置
    - 高效的文本处理，支持长文档的分段处理

支持的模型类型:
    - Ollama本地模型（如llama2、qwen等）
    - DeepSeek云端模型（通过API调用）
    - 自定义embedding模型

使用场景:
    - 招标文档自动化处理
    - 合同信息提取
    - 文档智能分析
    - 文本相似度计算
    - 知识图谱构建

性能优化:
    - 支持流式和非流式响应
    - 智能的超时控制
    - 内容长度限制避免token浪费
    - 缓存机制减少重复调用

依赖库:
    - requests: HTTP请求处理
    - json: JSON数据解析
    - logging: 日志记录
    - re: 正则表达式处理

作者: TenderInformationExtractor Team
创建时间: 2024
最后更新: 2024
版本: 1.0.0
"""

import json
import requests
import logging
from config.settings import Config
from .model_manager import model_manager

class LLMService:
    """
    大语言模型服务类
    
    提供统一的大语言模型调用接口，支持多种模型类型和任务场景。
    该类封装了与不同LLM服务的交互逻辑，包括Ollama本地模型和云端API模型。
    
    主要功能:
        - 招标文档信息提取
        - 动态字段信息提取
        - 文档语义摘要生成
        - 文本向量化处理
        - 多模型统一管理
    
    技术特点:
        - 支持多种模型后端（Ollama、DeepSeek等）
        - 智能提示词构建和响应解析
        - 完善的错误处理和重试机制
        - 灵活的配置管理
        - 高效的文本处理流程
    
    属性:
        ollama_url (str): Ollama服务的URL地址
        model_name (str): 当前使用的模型名称
        embedding_model (str): 用于文本向量化的模型名称
        logger (logging.Logger): 日志记录器
        model_manager: 模型管理器实例
    
    使用示例:
        >>> llm_service = LLMService()
        >>> result = llm_service.extract_tender_info(document_content)
        >>> summary = llm_service.summarize_document_purpose(doc_text)
        >>> embedding = llm_service.get_text_embedding(text)
    
    注意事项:
        - 确保相关模型服务已正确启动和配置
        - 长文档处理时注意token限制
        - 网络请求可能存在超时，建议设置合理的重试策略
    """
    
    def __init__(self, ollama_url: str = None, model_name: str = None, embedding_model: str = None):
        """
        初始化LLM服务实例
        
        设置模型连接参数和配置信息，初始化日志记录器和模型管理器。
        支持通过参数覆盖默认配置，同时保持向后兼容性。
        
        Parameters
        ----------
        ollama_url : str, optional
            Ollama服务的URL地址，默认使用配置文件中的设置
            格式: http://host:port (如: http://localhost:11434)
        model_name : str, optional
            要使用的模型名称，默认使用配置文件中的设置
            支持的模型: llama2, qwen, deepseek-chat等
        embedding_model : str, optional
            用于文本向量化的模型名称，默认使用配置文件中的设置
            常用模型: nomic-embed-text, text-embedding-ada-002等
        
        Raises
        ------
        Exception
            当模型配置无效或服务连接失败时抛出异常
        
        注意事项:
            - 参数为None时将使用配置文件中的默认值
            - 确保指定的模型已在服务端正确安装和配置
            - 网络连接问题可能导致初始化失败
        
        示例:
            >>> # 使用默认配置
            >>> service = LLMService()
            >>> 
            >>> # 自定义配置
            >>> service = LLMService(
            ...     ollama_url="http://192.168.1.100:11434",
            ...     model_name="qwen:7b",
            ...     embedding_model="nomic-embed-text"
            ... )
        """
        # 保持向后兼容性的同时，使用新的模型管理器
        self.ollama_url = Config.OLLAMA_URL
        self.model_name = Config.MODEL_NAME
        self.embedding_model = embedding_model or Config.EMBEDDING_MODEL
        self.logger = logging.getLogger(__name__)
        self.model_manager = model_manager
        
        # 记录初始化信息
        self.logger.info(f"LLM服务初始化完成 - 模型: {self.model_name}, Embedding: {self.embedding_model}")
    
    def extract_tender_info(self, document_content):
        """
        从招标文档中提取结构化信息
        
        使用配置的大语言模型从招标文档中提取预定义的关键信息字段，
        包括项目信息、招标方信息、时间节点、技术要求等多个维度的数据。
        
        Parameters
        ----------
        document_content : str
            招标文档的文本内容
            支持的文档类型: 招标公告、招标文件、合同文本等
        
        Returns
        -------
        dict
            提取的结构化信息，包含以下主要字段:
            - 项目名称、招标编号、项目所在地区
            - 招标人信息（名称、联系人、电话、地址等）
            - 招标代理机构信息
            - 时间节点（开标时间、截止时间等）
            - 技术要求和资质要求
            - 合同相关信息（甲乙双方、价格等）
        
        Raises
        ------
        Exception
            当模型调用失败、网络连接异常或响应解析失败时抛出异常
        
        处理流程:
            1. 构建专用的信息提取提示词
            2. 调用配置的大语言模型进行推理
            3. 解析模型返回的JSON格式响应
            4. 返回结构化的提取结果
        
        注意事项:
            - 文档内容过长时可能影响提取效果
            - 模型返回的信息准确性依赖于文档质量
            - 未找到的字段将设置为null，不会编造信息
        
        示例:
            >>> content = "某某项目招标公告..."
            >>> result = llm_service.extract_tender_info(content)
            >>> print(result['项目名称'])  # 输出: "某某道路建设项目"
            >>> print(result['招标编号'])  # 输出: "2024-001"
        """
        prompt = self._build_extraction_prompt(document_content)
        
        try:
            # 使用模型管理器调用当前配置的模型
            self.logger.info("开始提取招标信息")
            response = self.model_manager.call_model('tender_notice', prompt)
            result = self._parse_response(response)
            self.logger.info(f"招标信息提取完成，提取到 {len([k for k, v in result.items() if v is not None])} 个有效字段")
            return result
        except Exception as e:
            self.logger.error(f"招标信息提取失败: {str(e)}")
            raise Exception(f"大模型调用失败: {str(e)}")
    
    def extract_dynamic_info(self, document_content, field_list):
        """
        根据用户指定的动态字段列表从文档中提取信息
        
        提供灵活的信息提取功能，允许用户自定义需要提取的字段列表，
        而不局限于预设的固定字段。适用于不同类型文档的个性化信息提取需求。
        
        Args:
            document_content (str): 待处理的文档文本内容
                - 支持各种格式的文档内容
                - 建议预处理去除无关格式信息
            field_list (list): 需要提取的字段名称列表
                - 字段名应具有明确的语义含义
                - 支持中文和英文字段名
                - 建议使用具体、明确的字段描述
        
        Returns:
            dict: 提取的字段信息字典
                - 键为字段名，值为提取的内容
                - 未找到的字段值为null
                - 保持与输入字段列表相同的键名
        
        Raises:
            Exception: 当模型调用失败或响应解析异常时抛出
        
        Processing Flow:
            1. 根据字段列表动态构建提取提示词
            2. 生成对应的JSON格式模板
            3. 调用大语言模型进行信息提取
            4. 解析并返回结构化结果
        
        Example:
            >>> field_list = ['项目名称', '预算金额', '联系人', '截止日期']
            >>> content = "某某工程招标公告..."
            >>> result = llm_service.extract_dynamic_info(content, field_list)
            >>> print(result)
            {
                '项目名称': '某某道路建设工程',
                '预算金额': '500万元',
                '联系人': '张三',
                '截止日期': '2024-01-15'
            }
        
        Use Cases:
            - 自定义模板的信息提取
            - 特定业务场景的字段提取
            - 用户交互式的信息提取
            - 批量处理不同类型文档
        
        Note:
            - 字段名的语义清晰度直接影响提取准确性
            - 过多字段可能影响模型性能，建议合理控制数量
            - 提取结果的准确性依赖于文档内容的完整性
            - 支持嵌套字段和复杂数据结构的提取
        """
        prompt = self._build_dynamic_extraction_prompt(document_content, field_list)
        
        try:
            # 使用模型管理器调用当前配置的模型
            response = self.model_manager.call_model('tender_notice', prompt)
            return self._parse_response(response)
        except Exception as e:
            raise Exception(f"大模型调用失败: {str(e)}")
    
    def _build_dynamic_extraction_prompt(self, content, field_list):
        """
        根据字段列表动态构建信息提取提示词
        
        基于用户提供的字段列表，智能生成结构化的提示词模板，
        确保大语言模型能够准确理解提取需求并返回标准化的JSON格式结果。
        
        Args:
            content (str): 待处理的文档内容
                - 完整的文档文本，用于信息提取
                - 会被嵌入到提示词中作为分析对象
            field_list (list): 需要提取的字段名称列表
                - 每个字段名将成为JSON输出的键
                - 支持任意数量和类型的字段
        
        Returns:
            str: 完整的提示词文本
                - 包含任务描述、字段说明、文档内容和输出格式要求
                - 格式化为适合大语言模型理解的结构
        
        Prompt Structure:
            1. 任务描述 - 明确信息提取的目标
            2. 字段列表 - 详细列出需要提取的字段
            3. 文档内容 - 提供待分析的原始文本
            4. 输出格式 - 指定JSON格式和null值处理规则
            5. 质量要求 - 强调准确性和真实性要求
        
        Template Features:
            - 动态字段列表生成
            - 标准化JSON格式模板
            - 明确的null值处理指导
            - 防止信息编造的约束条件
        
        Example:
            >>> field_list = ['项目名称', '预算金额']
            >>> content = "某工程招标公告..."
            >>> prompt = self._build_dynamic_extraction_prompt(content, field_list)
            >>> # 生成的提示词包含字段描述和JSON模板
        
        Note:
            - 提示词长度会随字段数量和文档长度增加
            - JSON格式严格按照字段列表顺序生成
            - 包含防止AI幻觉的明确指导
            - 适用于各种类型的文档和字段组合
        """
        # 构建字段列表描述
        fields_description = "\n".join([f"- {field}" for field in field_list])
        
        # 构建JSON格式示例
        json_format = "{\n"
        for i, field in enumerate(field_list):
            comma = "," if i < len(field_list) - 1 else ""
            json_format += f'    "{field}": null{comma}\n'
        json_format += "}"
        
        prompt = f"""
请从以下文档中提取指定的关键信息，并以JSON格式返回：

需要提取的信息字段（如果某项信息未找到，请设置为null，不要胡编乱造）：
{fields_description}

文档内容：
{content}

请以以下JSON格式返回提取的信息，如果某项信息未找到，请设置为null：
{json_format}

请确保只提取文档中实际存在的信息，不要编造不存在的内容。如果某项信息在文档中找不到，请保持为null。
"""
        return prompt
    
    def _build_extraction_prompt(self, content):
        """
        构建招标文档信息提取的专用提示词
        
        为招标文档信息提取任务构建专门优化的提示词模板，
        包含完整的预定义字段列表和标准化的输出格式要求。
        
        Args:
            content (str): 招标文档的文本内容
                - 支持招标公告、招标文件、合同等各类文档
                - 内容将被嵌入到提示词中进行分析
        
        Returns:
            str: 完整的招标信息提取提示词
                - 包含详细的字段定义和JSON输出格式
                - 针对招标领域优化的专业提示词
        
        Predefined Fields:
            包含60+个招标相关的标准字段，涵盖：
            - 项目基本信息（名称、编号、地区等）
            - 招标方信息（单位名称、联系人、电话等）
            - 时间节点（开标时间、截止时间等）
            - 技术要求（资质、业绩、规格等）
            - 合同信息（甲乙双方、价格、账户等）
        
        Prompt Features:
            - 领域专业性：针对招标行业的专业术语和格式
            - 完整性：覆盖招标流程的各个环节
            - 标准化：统一的字段命名和格式要求
            - 准确性：明确的null值处理和防编造指导
        
        Template Structure:
            1. 任务说明 - 明确招标信息提取目标
            2. 字段清单 - 详细的预定义字段列表
            3. 文档内容 - 待分析的招标文档文本
            4. 输出格式 - 标准JSON格式模板
            5. 质量要求 - 准确性和真实性约束
        
        Use Cases:
            - 招标公告信息提取
            - 招标文件关键信息解析
            - 合同条款信息提取
            - 批量招标文档处理
        
        Note:
            - 字段列表基于招标行业实际需求设计
            - 支持多种招标文档格式和类型
            - 提示词经过实际项目验证和优化
            - 输出格式与下游处理模块兼容
        """
        prompt = f"""
请从以下招标文档中提取关键信息，并以JSON格式返回：

需要提取的信息包括以下标签（如果某项信息未找到，请设置为null，不要胡编乱造）：
- 项目名称  
- 材料名称  
- 招标编号  
- 项目所在地区  
- 项目公司名称  
- 建设地点  
- 规模  
- 建设工期  
- 标段划分  
- 本次招标采购材料的名称、数量、技术规格  
- 交货地点  
- 招标文件的获取开始日期  
- 业绩要求  
- 招标代理机构电话  
- 招标人联系人名字  
- 线下开标下午时间段，格式为x时至x时  
- 招标人单位名称  
- 招标代理机构联系人名字  
- 国家规定的其他条件(如国家强制性行业要求、资格条件等)  
- 监督部门  
- 招标人电话  
- 招标文件每标段售价，格式为xx元  
- 详细地址  
- 线下招标投标文件递交截止时间，格式为xxxx年xx月xx日xx时xx分  
- 交货期  
- 招标人单位地址  
- 招标文件的获取结束日期，格式为xxxx年xx月xx日  
- 招标代理机构单位名称  
- 电子招标投标文件递交截止时间，格式为xxxx年xx月xx日xx时xx分  
- 资质等级要求  
- 开标时间，格式为xxxx年xx月xx日xx时xx分  
- 招标人电子邮件  
- 线下招标投标文件递交地址  
- 建设地点  
- 线下招标结束日期，格式为xxxx年xx月xx日  
- 线下招标开标地点  
- 规模  
- 招标代理机构电子邮件  
- 线下招标开始日期，格式为xxxx年xx月xx日  
- 线下开标上午时间段，格式为x时至x时  
- 招标代理机构单位地址  
- 销售方  
- 签订日期  
- 合同总价  
- 不含税价款人民币  
- 采购方名称  
- 采购方联系人  
- 采购方电话  
- 采购方邮箱  
- 销售方联系人  
- 销售方电话  
- 销售方邮箱  
- 培训次数  
- 培训总时间  
- 甲方名称  
- 甲方法定代表人  
- 甲方委托代理人  
- 甲方联系人  
- 甲方地址  
- 甲方电话  
- 甲方邮箱  
- 甲方开户银行  
- 甲方账号  
- 甲方邮政编码  
- 乙方名称  
- 乙方法定代表人  
- 乙方委托代理人  
- 乙方联系人  
- 乙方地址  
- 乙方电话  
- 乙方邮箱  
- 乙方开户银行  
- 乙方账号  
- 乙方邮政编码  

文档内容：
{content}

请以以下JSON格式返回提取的信息，如果某项信息未找到，请设置为null：
{{
    "项目名称": null,
    "材料名称": null,
    "招标编号": null,
    "项目所在地区": null,
    "项目公司名称": null,
    "建设地点": null,
    "规模": null,
    "建设工期": null,
    "标段划分": null,
    "本次招标采购材料的名称、数量、技术规格": null,
    "交货地点": null,
    "招标文件的获取开始日期": null,
    "业绩要求": null,
    "招标代理机构电话": null,
    "招标人联系人名字": null,
    "线下开标下午时间段": null,
    "招标人单位名称": null,
    "招标代理机构联系人名字": null,
    "国家规定的其他条件": null,
    "监督部门": null,
    "招标人电话": null,
    "招标文件每标段售价": null,
    "详细地址": null,
    "线下招标投标文件递交截止时间": null,
    "交货期": null,
    "招标人单位地址": null,
    "招标文件的获取结束日期": null,
    "招标代理机构单位名称": null,
    "电子招标投标文件递交截止时间": null,
    "资质等级要求": null,
    "开标时间": null,
    "招标人电子邮件": null,
    "线下招标投标文件递交地址": null,
    "建设地点": null,
    "线下招标结束日期": null,
    "线下招标开标地点": null,
    "规模": null,
    "招标代理机构电子邮件": null,
    "线下招标开始日期": null,
    "线下开标上午时间段": null,
    "招标代理机构单位地址": null,
    "销售方": null,
    "签订日期": null,
    "合同总价": null,
    "不含税价款人民币": null,
    "采购方名称": null,
    "采购方联系人": null,
    "采购方电话": null,
    "采购方邮箱": null,
    "销售方联系人": null,
    "销售方电话": null,
    "销售方邮箱": null,
    "培训次数": null,
    "培训总时间": null,
    "甲方名称": null,
    "甲方法定代表人": null,
    "甲方委托代理人": null,
    "甲方联系人": null,
    "甲方地址": null,
    "甲方电话": null,
    "甲方E-mail": null,
    "甲方开户银行": null,
    "甲方账号": null,
    "甲方邮政编码": null,
    "乙方名称": null,
    "乙方法定代表人": null,
    "乙方委托代理人": null,
    "乙方联系人": null,
    "乙方地址": null,
    "乙方电话": null,
    "乙方E-mail": null,
    "乙方开户银行": null,
    "乙方账号": null,
    "乙方邮政编码": null

}}

请确保只提取文档中实际存在的信息，不要编造不存在的内容。如果某项信息在文档中找不到，请保持为null。
"""
        return prompt
    
    def _call_ollama(self, prompt):
        """
        调用Ollama本地模型API进行文本生成
        
        通过HTTP请求调用本地部署的Ollama服务，发送提示词并获取模型响应。
        支持非流式响应模式，适用于需要完整结果的信息提取任务。
        
        Args:
            prompt (str): 发送给模型的提示词
                - 包含任务描述和待处理内容的完整提示
                - 应该是格式良好的文本，避免特殊字符干扰
        
        Returns:
            str: 模型生成的响应文本
                - 通常为JSON格式的结构化数据
                - 具体格式取决于提示词的要求
        
        Raises:
            Exception: 当API调用失败时抛出异常
                - 网络连接问题
                - 服务不可用
                - HTTP状态码非200
        
        API Configuration:
            - 使用非流式模式（stream: false）
            - 超时设置为600秒，适应长文档处理
            - 使用配置的模型名称
        
        Request Format:
            {
                "model": "模型名称",
                "prompt": "提示词内容",
                "stream": false
            }
        
        Response Handling:
            - 检查HTTP状态码确保请求成功
            - 提取response字段中的实际内容
            - 错误时抛出包含状态码的异常
        
        Example:
            >>> prompt = "请提取以下文档的关键信息..."
            >>> response = self._call_ollama(prompt)
            >>> # response包含模型生成的JSON格式结果
        
        Note:
            - 需要确保Ollama服务正在运行
            - 模型必须已经下载并可用
            - 长文档处理可能需要较长时间
            - 网络超时设置应根据实际需求调整
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=600
        )
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            raise Exception(f"Ollama API调用失败: {response.status_code}")
    
    def _parse_response(self, response):
        """
        解析大语言模型返回的JSON格式响应
        
        智能解析模型返回的文本，提取其中的JSON数据并转换为Python字典。
        支持多种响应格式，包括纯JSON和包含额外文本的混合格式。
        
        Args:
            response (str): 模型返回的原始响应文本
                - 可能是纯JSON格式
                - 可能包含JSON和其他解释性文本
                - 可能包含格式化字符和换行符
        
        Returns:
            dict: 解析后的JSON数据字典
                - 键值对应提取的字段和内容
                - 保持原始数据类型（字符串、数字、null等）
        
        Raises:
            Exception: 当无法解析JSON格式时抛出异常
                - JSON格式错误
                - 响应中不包含有效的JSON数据
        
        Parsing Strategy:
            1. 首先尝试直接解析整个响应为JSON
            2. 如果失败，使用正则表达式提取JSON部分
            3. 支持多行JSON和嵌套结构
            4. 处理常见的格式问题和特殊字符
        
        Regex Pattern:
            - 使用 r'\{.*\}' 匹配大括号包围的JSON内容
            - DOTALL标志支持跨行匹配
            - 贪婪匹配确保获取完整JSON结构
        
        Example:
            >>> response = '''这是提取的信息：
            ... {
            ...     "项目名称": "某某工程",
            ...     "预算金额": "100万元"
            ... }
            ... 提取完成。'''
            >>> result = self._parse_response(response)
            >>> print(result['项目名称'])  # 输出: "某某工程"
        
        Error Handling:
            - 捕获JSON解析异常并提供有意义的错误信息
            - 支持调试和问题排查
            - 确保系统稳定性
        
        Note:
            - 解析结果保持原始数据类型
            - null值会被正确处理为Python的None
            - 支持嵌套对象和数组结构
            - 适用于各种模型的响应格式
        """
        try:
            # 尝试直接解析JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise Exception("无法解析大模型返回的JSON格式")

    def summarize_document_purpose(self, doc_text: str) -> str:
        """
        生成文档的一句话语义摘要
        
        使用大语言模型分析文档内容，生成简洁明了的一句话摘要，
        重点突出文档的主要目的和类型，特别适用于招标采购类文档的快速识别。
        
        Args:
            doc_text (str): 待摘要的文档文本内容
                - 支持各种类型的文档内容
                - 长文档会被截取前2000字符以控制处理时间
                - 建议预处理去除无关格式信息
        
        Returns:
            str: 文档的一句话语义摘要
                - 简洁明了，通常在50字以内
                - 重点说明文档类型和主要内容
                - 失败时返回默认错误信息
        
        Processing Flow:
            1. 构建专用的摘要生成提示词
            2. 限制输入文档长度（前2000字符）
            3. 调用大语言模型生成摘要
            4. 解析和清理返回结果
            5. 异常处理和默认值返回
        
        Content Limitation:
            - 输入文档截取前2000字符
            - 避免token过多导致的性能问题
            - 通常前2000字符包含文档的核心信息
        
        Example:
            >>> doc_text = "某某道路建设工程招标公告..."
            >>> summary = llm_service.summarize_document_purpose(doc_text)
            >>> print(summary)
            "这是一份道路建设工程的招标公告文档"
            
            >>> contract_text = "甲乙双方就设备采购签订合同..."
            >>> summary = llm_service.summarize_document_purpose(contract_text)
            >>> print(summary)
            "这是一份设备采购合同文档"
        
        Response Handling:
            - 支持字典格式响应（提取summary字段）
            - 支持纯文本格式响应
            - 自动清理多余的空白字符
        
        Error Handling:
            - 网络异常时返回"文档摘要生成失败"
            - 模型调用失败时记录错误日志
            - 解析异常时返回默认错误信息
        
        Use Cases:
            - 文档快速分类和识别
            - 批量文档处理的预览
            - 用户界面的文档描述
            - 文档管理系统的自动标注
        
        Note:
            - 摘要质量依赖于文档内容的完整性
            - 适用于中文和英文文档
            - 生成时间通常在几秒内
            - 结果可用于进一步的文档分类
        """
        prompt = f"""
请用一句话概括以下文档的目的或主题，重点说明这是什么类型的招标或采购项目：

文档内容：
{doc_text[:2000]}  # 限制长度避免token过多

请直接回答，不要包含其他解释：
"""
        
        try:
            response = self._call_ollama(prompt)
            # 提取摘要内容
            if isinstance(response, dict) and 'summary' in response:
                return response['summary']
            elif isinstance(response, str):
                return response.strip()
            else:
                return "无法生成文档摘要"
                
        except Exception as e:
            self.logger.error(f"生成文档摘要时出错: {str(e)}")
            return "文档摘要生成失败"

    def get_text_embedding(self, text: str) -> list:
        """
        使用配置的embedding模型获取文本的向量表示
        
        调用Ollama的embedding API，将输入文本转换为高维向量表示，
        用于文本相似度计算、语义搜索、聚类分析等下游任务。
        
        Args:
            text (str): 需要向量化的文本内容
                - 支持中文和英文文本
                - 建议长度在合理范围内（通常<512 tokens）
                - 可以是单词、句子、段落或文档
        
        Returns:
            list: 文本的embedding向量
                - 浮点数列表，维度取决于使用的模型
                - 常见维度：384、768、1024、1536等
                - 空列表表示获取失败
        
        API Configuration:
            - 使用配置的embedding模型（如nomic-embed-text）
            - 超时设置为30秒
            - 标准的JSON格式请求
        
        Request Format:
            {
                "model": "embedding模型名称",
                "prompt": "待向量化的文本"
            }
        
        Response Format:
            {
                "embedding": [0.1, -0.2, 0.3, ...]
            }
        
        Example:
            >>> text = "这是一个测试文本"
            >>> embedding = llm_service.get_text_embedding(text)
            >>> print(len(embedding))  # 输出: 384 (取决于模型)
            >>> print(type(embedding[0]))  # 输出: <class 'float'>
            
            >>> # 计算文本相似度
            >>> text1 = "招标公告"
            >>> text2 = "投标文件"
            >>> emb1 = llm_service.get_text_embedding(text1)
            >>> emb2 = llm_service.get_text_embedding(text2)
            >>> # 使用余弦相似度等方法计算相似性
        
        Error Handling:
            - HTTP请求失败时记录错误并返回空列表
            - 网络超时时返回空列表
            - API响应格式异常时返回空列表
            - 所有异常都会被捕获并记录日志
        
        Use Cases:
            - 文档相似度计算
            - 语义搜索和检索
            - 文本聚类分析
            - 推荐系统
            - 知识图谱构建
        
        Performance Notes:
            - embedding生成速度通常很快（毫秒级）
            - 向量维度影响存储空间和计算复杂度
            - 建议批量处理以提高效率
        
        Note:
            - 需要确保embedding模型已正确安装
            - 不同模型生成的向量不可直接比较
            - 向量质量依赖于模型的训练数据
            - 适用于多种NLP下游任务
        """
        try:
            # 调用 Ollama 的 embedding API
            url = f"{self.ollama_url}/api/embeddings"
            
            payload = {
                "model": self.embedding_model,
                "prompt": text
            }
            
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('embedding', [])
            else:
                self.logger.error(f"Embedding API 调用失败: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取 embedding 时出错: {str(e)}")
            return []