# LLM相关辅助函数
import json
import re
from typing import Dict, List, Any, Optional

def validate_json_response(response: str) -> bool:
    """
    验证响应是否为有效的JSON格式
    
    检查大语言模型返回的响应字符串是否符合JSON格式规范。
    该函数用于在解析LLM响应前进行格式验证，确保后续处理的安全性。
    
    Parameters
    ----------
    response : str
        LLM返回的响应字符串
        
    Returns
    -------
    bool
        如果响应是有效的JSON格式返回True，否则返回False
        
    验证策略
    --------
    - 使用json.loads()进行严格的JSON格式检查
    - 捕获JSONDecodeError异常以判断格式有效性
    - 不对JSON内容进行语义验证，仅检查格式
    
    示例
    ----
    >>> validate_json_response('{"name": "test", "value": 123}')
    True
    >>> validate_json_response('invalid json string')
    False
    >>> validate_json_response('[1, 2, 3]')
    True
    
    使用场景
    --------
    - LLM响应预处理
    - 数据格式验证
    - 错误处理前置检查
    - API响应验证
    
    注意事项
    --------
    - 仅验证JSON格式，不验证内容结构
    - 空字符串会被视为无效JSON
    - 支持JSON对象和数组格式
    """
    try:
        json.loads(response)
        return True
    except json.JSONDecodeError:
        return False

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    从文本中提取JSON内容
    
    智能提取文本中的JSON数据，支持从混合内容中解析出有效的JSON对象。
    该函数采用多层次解析策略，优先尝试直接解析，失败时使用正则表达式提取。
    
    Parameters
    ----------
    text : str
        包含JSON内容的文本字符串，可能包含其他非JSON内容
        
    Returns
    -------
    Optional[Dict[str, Any]]
        成功提取的JSON对象，如果提取失败返回None
        
    提取策略
    --------
    1. 直接解析：首先尝试将整个文本作为JSON解析
    2. 正则提取：使用正则表达式匹配大括号包围的JSON片段
    3. 递归解析：对提取的片段再次进行JSON解析
    4. 失败处理：所有策略失败时返回None
    
    正则表达式
    ----------
    - 模式：r'\{.*\}'
    - 标志：re.DOTALL（匹配换行符）
    - 匹配：从第一个'{'到最后一个'}'的内容
    
    示例
    ----
    >>> extract_json_from_text('{"name": "test"}')
    {'name': 'test'}
    >>> extract_json_from_text('前缀文本 {"key": "value"} 后缀文本')
    {'key': 'value'}
    >>> extract_json_from_text('无效内容')
    None
    
    使用场景
    --------
    - LLM响应解析
    - 混合格式文本处理
    - 容错性JSON提取
    - 数据清洗和预处理
    
    注意事项
    --------
    - 仅返回字典类型的JSON对象
    - 不支持JSON数组的提取
    - 嵌套大括号可能影响提取准确性
    - 建议配合validate_json_response使用
    """
    try:
        # 尝试直接解析
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试提取JSON部分
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return None

def clean_field_value(value: Any) -> Any:
    """
    清理字段值，移除多余的空白字符
    
    对提取的字段值进行标准化清理，主要处理字符串类型的空白字符问题。
    该函数确保数据的一致性和可用性，避免因格式问题导致的数据质量下降。
    
    Parameters
    ----------
    value : Any
        原始字段值，可以是任意类型
        
    Returns
    -------
    Any
        清理后的字段值，字符串类型会被处理，其他类型原样返回
        
    清理规则
    --------
    - 字符串类型：移除首尾空白，合并内部多个空白字符为单个空格
    - 空字符串：清理后如果为空则返回None
    - 非字符串：原样返回，不进行任何处理
    - None值：保持None状态
    
    正则表达式
    ----------
    - 模式：r'\s+'
    - 替换：单个空格字符
    - 作用：将连续的空白字符（空格、制表符、换行符等）合并为单个空格
    
    示例
    ----
    >>> clean_field_value('  hello   world  ')
    'hello world'
    >>> clean_field_value('\t\n  text  \n\t')
    'text'
    >>> clean_field_value('')
    None
    >>> clean_field_value('   ')
    None
    >>> clean_field_value(123)
    123
    >>> clean_field_value(None)
    None
    
    使用场景
    --------
    - 数据提取后的清理
    - 字段值标准化
    - 数据质量保证
    - 存储前的预处理
    
    注意事项
    --------
    - 仅处理字符串类型，其他类型保持不变
    - 清理后的空字符串会转换为None
    - 保留字符串内部的单个空格
    - 不会改变原始数据的语义含义
    """
    if isinstance(value, str):
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', value.strip())
        # 如果清理后为空字符串，返回None
        return cleaned if cleaned else None
    return value

def validate_extracted_fields(extracted_data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    验证和清理提取的字段数据
    
    对从文档中提取的字段数据进行验证和标准化处理，确保数据质量和完整性。
    该函数会根据必需字段列表筛选数据，并对每个字段值进行清理。
    
    Parameters
    ----------
    extracted_data : Dict[str, Any]
        从文档中提取的原始数据字典
    required_fields : List[str]
        必需的字段名称列表，用于筛选和验证数据
        
    Returns
    -------
    Dict[str, Any]
        验证和清理后的数据字典，只包含必需字段
        
    处理流程
    --------
    1. 遍历必需字段列表
    2. 从提取数据中获取对应字段值
    3. 对每个字段值调用clean_field_value进行清理
    4. 构建清理后的数据字典
    5. 返回标准化的结果
    
    数据清理
    --------
    - 字符串值：移除多余空白字符
    - 空值处理：空字符串转换为None
    - 缺失字段：设置为None
    - 类型保持：非字符串类型保持原样
    
    示例
    ----
    >>> data = {'name': '  张三  ', 'age': 25, 'extra': 'unused'}
    >>> fields = ['name', 'age', 'address']
    >>> validate_extracted_fields(data, fields)
    {'name': '张三', 'age': 25, 'address': None}
    
    >>> data = {'title': '\t项目标题\n', 'amount': ''}
    >>> fields = ['title', 'amount']
    >>> validate_extracted_fields(data, fields)
    {'title': '项目标题', 'amount': None}
    
    使用场景
    --------
    - 文档信息提取后的数据处理
    - 字段标准化和验证
    - 数据质量保证
    - 模板填充前的预处理
    
    注意事项
    --------
    - 只返回必需字段，忽略额外字段
    - 缺失的必需字段会被设置为None
    - 依赖clean_field_value函数进行值清理
    - 保持字段顺序与required_fields一致
    """
    cleaned_data = {}
    
    for field in required_fields:
        value = extracted_data.get(field)
        cleaned_data[field] = clean_field_value(value)
    
    return cleaned_data

def build_prompt_template(template_type: str, **kwargs) -> str:
    """
    构建提示词模板
    
    根据指定的模板类型和参数构建用于大语言模型的提示词。
    该函数提供了多种预定义模板，支持灵活的参数替换和自定义。
    
    Parameters
    ----------
    template_type : str
        模板类型，支持以下选项：
        - 'extraction': 信息提取模板
        - 'summary': 文档摘要模板
        - 'dynamic': 动态字段提取模板
    **kwargs
        模板参数，用于填充模板中的占位符
        
    Returns
    -------
    str
        构建完成的提示词字符串
        
    模板类型说明
    ----------
    extraction模板：
    - 用途：从文档中提取预定义的关键信息
    - 参数：content（文档内容）
    - 输出：JSON格式的提取结果
    
    summary模板：
    - 用途：生成文档的一句话摘要
    - 参数：content（文档内容）
    - 输出：简洁的文档主题描述
    
    dynamic模板：
    - 用途：根据指定字段动态提取信息
    - 参数：fields（字段列表）、content（文档内容）
    - 输出：JSON格式的指定字段提取结果
    
    示例
    ----
    >>> # 信息提取模板
    >>> prompt = build_prompt_template('extraction', content='文档内容')
    
    >>> # 摘要生成模板
    >>> prompt = build_prompt_template('summary', content='文档内容')
    
    >>> # 动态字段提取模板
    >>> prompt = build_prompt_template('dynamic', 
    ...                               fields=['项目名称', '预算金额'],
    ...                               content='文档内容')
    
    模板特性
    --------
    - 预定义格式：确保提示词的一致性和有效性
    - 参数化设计：支持灵活的内容替换
    - 默认回退：未知类型使用extraction模板
    - JSON输出：引导模型生成结构化数据
    
    使用场景
    --------
    - LLM接口调用前的提示词准备
    - 不同任务类型的模板管理
    - 提示词标准化和复用
    - 批量处理任务的模板生成
    
    注意事项
    --------
    - 模板参数必须与占位符匹配
    - 未知模板类型会使用默认的extraction模板
    - 建议根据具体任务调整模板内容
    - 模板设计影响模型输出质量
    """
    templates = {
        'extraction': """
请从以下文档中提取关键信息，并以JSON格式返回：

文档内容：
{content}

请以JSON格式返回提取的信息，如果某项信息未找到，请设置为null。
""",
        'summary': """
请用一句话概括以下文档的目的或主题：

文档内容：
{content}

请直接回答，不要包含其他解释。
""",
        'dynamic': """
请从以下文档中提取指定的关键信息，并以JSON格式返回：

需要提取的信息字段：
{fields}

文档内容：
{content}

请以JSON格式返回提取的信息，如果某项信息未找到，请设置为null。
"""
    }
    
    template = templates.get(template_type, templates['extraction'])
    return template.format(**kwargs)

def calculate_extraction_confidence(extracted_data: Dict[str, Any]) -> float:
    """
    计算提取结果的置信度
    
    基于字段填充率计算信息提取结果的置信度分数。
    该函数通过统计有效字段与总字段的比例来评估提取质量。
    
    Parameters
    ----------
    extracted_data : Dict[str, Any]
        提取的数据字典，包含各个字段及其值
        
    Returns
    -------
    float
        置信度分数，范围为0.0到1.0
        - 1.0：所有字段都有有效值
        - 0.0：没有任何有效字段或数据为空
        
    计算方法
    --------
    置信度 = 有效字段数 / 总字段数
    
    有效字段判断标准：
    - 值不为None
    - 值不为空字符串
    - 其他类型的值都视为有效
    
    示例
    ----
    >>> data = {'name': '张三', 'age': 25, 'address': None}
    >>> calculate_extraction_confidence(data)
    0.6666666666666666  # 2/3
    
    >>> data = {'title': '项目A', 'amount': '100万', 'date': '2024-01-01'}
    >>> calculate_extraction_confidence(data)
    1.0  # 3/3
    
    >>> data = {'field1': None, 'field2': '', 'field3': None}
    >>> calculate_extraction_confidence(data)
    0.0  # 0/3
    
    >>> data = {}
    >>> calculate_extraction_confidence(data)
    0.0  # 空数据
    
    使用场景
    --------
    - 提取质量评估
    - 结果可信度判断
    - 自动化质量控制
    - 性能监控和统计
    
    计算特点
    --------
    - 简单直观的比例计算
    - 不考虑字段重要性权重
    - 适用于快速质量评估
    - 结果易于理解和比较
    
    注意事项
    --------
    - 仅基于字段填充率，不评估内容准确性
    - 所有字段权重相等
    - 空数据返回0.0置信度
    - 建议结合人工审核使用
    """
    if not extracted_data:
        return 0.0
    
    total_fields = len(extracted_data)
    filled_fields = sum(1 for value in extracted_data.values() if value is not None and value != "")
    
    return filled_fields / total_fields if total_fields > 0 else 0.0

def format_extraction_result(extracted_data: Dict[str, Any], confidence: float = None) -> Dict[str, Any]:
    """
    格式化提取结果
    
    将原始的提取数据格式化为标准的结果结构，包含数据统计和质量评估信息。
    该函数为提取结果添加元数据，便于后续处理和质量监控。
    
    Parameters
    ----------
    extracted_data : Dict[str, Any]
        从文档中提取的原始数据字典
    confidence : float, optional
        预计算的置信度分数，如果未提供则自动计算
        
    Returns
    -------
    Dict[str, Any]
        格式化后的结果字典，包含以下字段：
        - extracted_fields (Dict[str, Any]): 原始提取的字段数据
        - total_fields (int): 总字段数量
        - filled_fields (int): 有效填充的字段数量
        - confidence (float): 置信度分数（0.0-1.0）
        
    结果结构
    --------
    {
        "extracted_fields": {原始提取数据},
        "total_fields": 总字段数,
        "filled_fields": 有效字段数,
        "confidence": 置信度分数
    }
    
    统计计算
    --------
    - total_fields: 提取数据字典的键数量
    - filled_fields: 非None且非空字符串的字段数量
    - confidence: 有效字段比例或传入的预计算值
    
    示例
    ----
    >>> data = {'name': '张三', 'age': 25, 'address': None}
    >>> result = format_extraction_result(data)
    >>> print(result)
    {
        'extracted_fields': {'name': '张三', 'age': 25, 'address': None},
        'total_fields': 3,
        'filled_fields': 2,
        'confidence': 0.6666666666666666
    }
    
    >>> # 使用预计算的置信度
    >>> result = format_extraction_result(data, confidence=0.8)
    >>> print(result['confidence'])  # 0.8
    
    使用场景
    --------
    - API响应格式化
    - 结果质量评估
    - 数据处理管道
    - 性能监控和日志记录
    
    格式化优势
    ----------
    - 统一的结果结构
    - 内置质量评估
    - 便于后续处理
    - 支持批量分析
    
    注意事项
    --------
    - 保留原始提取数据不变
    - 自动计算统计信息
    - 支持自定义置信度覆盖
    - 适用于各种提取任务类型
    """
    result = {
        'extracted_fields': extracted_data,
        'total_fields': len(extracted_data),
        'filled_fields': sum(1 for value in extracted_data.values() if value is not None and value != "")
    }
    
    if confidence is not None:
        result['confidence'] = confidence
    else:
        result['confidence'] = calculate_extraction_confidence(extracted_data)
    
    return result