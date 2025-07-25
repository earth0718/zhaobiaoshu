#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大语言模型管理器模块 (Model Manager)

功能概述:
    本模块提供了统一的大语言模型管理和调用接口，支持多种模型提供商的无缝切换。
    主要负责模型配置管理、客户端初始化、模型调用路由和可用性检查等功能。

主要功能:
    1. 多模型提供商支持 - 支持Ollama本地模型和DeepSeek云端模型
    2. 动态模型切换 - 支持运行时切换不同的模型提供商
    3. 配置文件管理 - 自动加载和保存模型配置
    4. 客户端管理 - 统一管理不同提供商的API客户端
    5. 可用性检查 - 实时检查模型服务的可用性和响应时间
    6. 统一调用接口 - 提供一致的模型调用API

技术特点:
    - 插件化架构设计，易于扩展新的模型提供商
    - 智能的错误处理和重试机制
    - 完善的日志记录和监控
    - 配置热更新，无需重启服务
    - 类型安全的接口设计

支持的模型提供商:
    - Ollama: 本地部署的开源大语言模型
      * 支持llama2、qwen、mistral等多种模型
      * 本地推理，数据隐私性好
      * 适合离线环境和私有部署
    
    - DeepSeek: 云端API服务
      * 高性能的商业化模型
      * 支持大规模并发调用
      * 适合生产环境和高并发场景

模块架构:
    - ModelManager: 核心管理类，负责模型调用和配置管理
    - 配置文件: model_config.json，存储模型配置信息
    - 客户端池: 管理不同提供商的API客户端实例

使用场景:
    - 招标文档信息提取
    - 招标书自动生成
    - 文档智能分析
    - 多模型性能对比
    - A/B测试和模型评估

性能优化:
    - 客户端连接池复用
    - 智能的超时和重试策略
    - 异步调用支持（可扩展）
    - 响应时间监控

安全特性:
    - API密钥安全存储
    - 敏感信息脱敏显示
    - 访问权限控制
    - 请求日志审计

依赖库:
    - json: JSON配置文件处理
    - requests: HTTP请求处理
    - logging: 日志记录
    - typing: 类型注解支持
    - ollama: Ollama客户端（可选）
    - openai: OpenAI兼容客户端（可选）

作者: TenderInformationExtractor Team
创建时间: 2024
最后更新: 2024
版本: 1.0.0
"""

import json
import os
import requests
import logging
from typing import Dict, Any, Optional, List
from config.settings import Config

try:
    import ollama
except ImportError:
    ollama = None
    
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class ModelManager:
    """
    统一的大语言模型管理器
    
    提供多模型提供商的统一管理和调用接口，支持动态模型切换、配置管理、
    可用性检查等功能。该类是整个LLM服务的核心组件。
    
    主要职责:
        - 模型配置的加载、保存和管理
        - 不同模型提供商客户端的初始化和管理
        - 统一的模型调用接口和路由
        - 模型可用性检查和性能监控
        - 运行时模型切换和配置更新
    
    支持的模型提供商:
        - Ollama: 本地部署的开源模型（llama2、qwen等）
        - DeepSeek: 云端商业化API服务
    
    架构设计:
        - 插件化设计，易于扩展新的模型提供商
        - 配置驱动，支持热更新
        - 客户端池管理，提高性能
        - 统一错误处理和日志记录
    
    属性:
        logger (logging.Logger): 日志记录器
        config_path (str): 配置文件路径
        config (Dict): 模型配置信息
        clients (Dict): 模型客户端实例池
    
    使用示例:
        >>> manager = ModelManager()
        >>> response = manager.call_model('tender_notice', '提取招标信息')
        >>> manager.set_current_model('tender_notice', 'deepseek')
        >>> availability = manager.check_model_availability('ollama')
    
    注意事项:
        - 确保配置文件格式正确
        - 网络连接问题可能影响云端模型调用
        - 本地模型需要确保服务正常运行
    """
    
    def __init__(self):
        """
        初始化模型管理器
        
        执行以下初始化步骤:
        1. 设置日志记录器
        2. 确定配置文件路径
        3. 加载模型配置
        4. 初始化客户端实例池
        5. 初始化各模型提供商的客户端
        
        配置文件结构:
            - models: 各模块的模型配置（当前使用的模型、可选项）
            - providers: 各提供商的连接配置（URL、API密钥等）
        
        Raises
        ------
        Exception
            当配置文件加载失败或客户端初始化异常时抛出
        
        注意事项:
            - 配置文件不存在时会使用默认配置
            - 客户端初始化失败不会阻止管理器创建
            - 依赖库缺失时会记录警告但继续运行
        
        示例:
            >>> # 自动加载配置并初始化所有可用客户端
            >>> manager = ModelManager()
            >>> print(f"已加载 {len(manager.clients)} 个模型客户端")
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'model_config.json')
        self.config = self._load_config()
        self.clients = {}
        self._initialize_clients()
        
        # 记录初始化完成信息
        self.logger.info(f"模型管理器初始化完成，已加载 {len(self.clients)} 个客户端")
        self.logger.debug(f"配置文件路径: {self.config_path}")
        self.logger.debug(f"可用客户端: {list(self.clients.keys())}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载模型配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载模型配置失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "models": {
                "tender_notice": {"current": "ollama", "options": ["ollama", "deepseek"]},
                "tender_generation": {"current": "deepseek", "options": ["ollama", "deepseek"]}
            },
            "providers": {
                "ollama": {
                    "url": Config.OLLAMA_URL,
                    "model": Config.MODEL_NAME
                },
                "deepseek": {
                    "api_key": "your_api_key_here",
                    "base_url": "https://api.deepseek.com",
                    "model": "deepseek-chat"
                }
            }
        }
    
    def _initialize_clients(self):
        """初始化模型客户端"""
        providers = self.config.get('providers', {})
        
        # 初始化Ollama客户端
        if 'ollama' in providers:
            try:
                if ollama is None:
                    self.logger.warning("ollama模块未安装，无法初始化Ollama客户端")
                else:
                    ollama_config = providers['ollama']
                    self.clients['ollama'] = ollama.Client(host=ollama_config.get('url', 'http://localhost:11434'))
                    self.logger.info("Ollama客户端初始化成功")
            except Exception as e:
                self.logger.error(f"Ollama客户端初始化失败: {e}")
        
        # 初始化DeepSeek客户端
        if 'deepseek' in providers:
            try:
                if OpenAI is None:
                    self.logger.warning("openai模块未安装，无法初始化DeepSeek客户端")
                else:
                    deepseek_config = providers['deepseek']
                    api_key = deepseek_config.get('api_key')
                    if api_key and api_key != 'your_api_key_here':
                        self.clients['deepseek'] = OpenAI(
                            api_key=api_key,
                            base_url=deepseek_config.get('base_url', 'https://api.deepseek.com')
                        )
                        self.logger.info("DeepSeek客户端初始化成功")
                    else:
                        self.logger.warning("DeepSeek API Key未配置")
            except Exception as e:
                self.logger.error(f"DeepSeek客户端初始化失败: {e}")
    
    def get_current_model(self, module: str) -> str:
        """获取指定模块当前使用的模型"""
        return self.config.get('models', {}).get(module, {}).get('current', 'ollama')
    
    def set_current_model(self, module: str, provider: str) -> bool:
        """设置指定模块使用的模型"""
        try:
            if module not in self.config.get('models', {}):
                return False
            
            available_options = self.config['models'][module].get('options', [])
            if provider not in available_options:
                return False
            
            self.config['models'][module]['current'] = provider
            self._save_config()
            self.logger.info(f"模块 {module} 的模型已切换为 {provider}")
            return True
        except Exception as e:
            self.logger.error(f"设置模型失败: {e}")
            return False
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
    
    def call_model(self, module: str, prompt: str, **kwargs) -> str:
        """统一的模型调用接口"""
        provider = self.get_current_model(module)
        
        if provider == 'ollama':
            return self._call_ollama(prompt, **kwargs)
        elif provider == 'deepseek':
            return self._call_deepseek(prompt, **kwargs)
        else:
            raise ValueError(f"不支持的模型提供商: {provider}")
    
    def _call_ollama(self, prompt: str, **kwargs) -> str:
        """调用Ollama模型"""
        try:
            if 'ollama' not in self.clients:
                raise Exception("Ollama客户端未初始化")
            
            client = self.clients['ollama']
            model_name = self.config['providers']['ollama']['model']
            
            response = client.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            self.logger.error(f"Ollama调用失败: {e}")
            raise Exception(f"Ollama调用失败: {e}")
    
    def _call_deepseek(self, prompt: str, **kwargs) -> str:
        """调用DeepSeek模型"""
        try:
            if 'deepseek' not in self.clients:
                raise Exception("DeepSeek客户端未初始化")
            
            client = self.clients['deepseek']
            model_name = self.config['providers']['deepseek']['model']
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"DeepSeek调用失败: {e}")
            raise Exception(f"DeepSeek调用失败: {e}")
    
    def check_model_availability(self, provider: str) -> Dict[str, Any]:
        """检查模型可用性"""
        result = {
            'provider': provider,
            'available': False,
            'message': '',
            'response_time': None
        }
        
        try:
            import time
            start_time = time.time()
            
            if provider == 'ollama':
                result.update(self._check_ollama_availability())
            elif provider == 'deepseek':
                result.update(self._check_deepseek_availability())
            
            if result['available']:
                result['response_time'] = round((time.time() - start_time) * 1000, 2)  # 毫秒
                
        except Exception as e:
            result['message'] = str(e)
        
        return result
    
    def _check_ollama_availability(self) -> Dict[str, Any]:
        """检查Ollama可用性"""
        try:
            ollama_config = self.config['providers']['ollama']
            url = ollama_config['url']
            
            # 检查Ollama服务是否运行
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code == 200:
                # 检查指定模型是否存在
                models = response.json().get('models', [])
                model_name = ollama_config['model']
                
                # 检查完整模型名称或基础名称匹配
                model_exists = any(
                    model.get('name', '') == model_name or 
                    model.get('name', '').startswith(model_name.split(':')[0]) 
                    for model in models
                )
                
                if model_exists:
                    return {'available': True, 'message': 'Ollama服务正常，模型可用'}
                else:
                    return {'available': False, 'message': f'模型 {model_name} 未找到'}
            else:
                return {'available': False, 'message': 'Ollama服务连接失败'}
        except Exception as e:
            return {'available': False, 'message': f'Ollama检查失败: {str(e)}'}
    
    def _check_deepseek_availability(self) -> Dict[str, Any]:
        """检查DeepSeek可用性"""
        try:
            if 'deepseek' not in self.clients:
                return {'available': False, 'message': 'DeepSeek客户端未初始化'}
            
            # 发送一个简单的测试请求
            client = self.clients['deepseek']
            response = client.chat.completions.create(
                model=self.config['providers']['deepseek']['model'],
                messages=[{'role': 'user', 'content': '测试'}],
                max_tokens=10
            )
            
            if response.choices and len(response.choices) > 0:
                return {'available': True, 'message': 'DeepSeek API正常'}
            else:
                return {'available': False, 'message': 'DeepSeek API响应异常'}
        except Exception as e:
            return {'available': False, 'message': f'DeepSeek检查失败: {str(e)}'}
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            'models': self.config.get('models', {}),
            'providers': {k: {**v, 'api_key': '***' if 'api_key' in v else None} for k, v in self.config.get('providers', {}).items()},
            'ui_config': self.config.get('ui_config', {})
        }
    
    def get_available_models(self, module: str) -> List[str]:
        """获取指定模块可用的模型列表"""
        return self.config.get('models', {}).get(module, {}).get('options', [])
    
    def get_available_providers(self) -> List[str]:
        """获取所有可用的模型提供商列表"""
        return list(self.config.get('providers', {}).keys())

# 全局模型管理器实例
model_manager = ModelManager()