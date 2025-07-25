#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama性能优化脚本
用于提升本地大模型的生成速度和响应性能
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class OllamaOptimizer:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.api_base = f"{host}/api"
        
    def check_ollama_status(self) -> bool:
        """检查Ollama服务状态"""
        try:
            response = requests.get(f"{self.api_base}/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ollama服务未运行: {e}")
            return False
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """获取模型信息"""
        try:
            response = requests.get(f"{self.api_base}/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if model['name'].lower() == model_name.lower():
                        return model
            return {}
        except Exception as e:
            print(f"❌ 获取模型信息失败: {e}")
            return {}
    
    def preload_model(self, model_name: str) -> bool:
        """预加载模型到内存中"""
        print(f"🔄 正在预加载模型 {model_name}...")
        try:
            # 发送一个简单的请求来预热模型
            payload = {
                "model": model_name,
                "prompt": "你好",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 10
                }
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                load_time = time.time() - start_time
                print(f"✅ 模型预加载完成，耗时: {load_time:.2f}秒")
                return True
            else:
                print(f"❌ 模型预加载失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 模型预加载异常: {e}")
            return False
    
    def test_model_performance(self, model_name: str, test_prompt: str = "请简要介绍人工智能的发展历程") -> Dict[str, float]:
        """测试模型性能"""
        print(f"🧪 正在测试模型 {model_name} 的性能...")
        
        payload = {
            "model": model_name,
            "prompt": test_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 200
            }
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/generate",
                json=payload,
                timeout=120
            )
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                token_count = len(response_text.split())
                tokens_per_second = token_count / total_time if total_time > 0 else 0
                
                performance = {
                    'total_time': total_time,
                    'token_count': token_count,
                    'tokens_per_second': tokens_per_second
                }
                
                print(f"📊 性能测试结果:")
                print(f"   总耗时: {total_time:.2f}秒")
                print(f"   生成token数: {token_count}")
                print(f"   生成速度: {tokens_per_second:.2f} tokens/秒")
                
                return performance
            else:
                print(f"❌ 性能测试失败: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ 性能测试异常: {e}")
            return {}
    
    def optimize_system_settings(self):
        """输出系统优化建议"""
        print("\n🚀 Ollama性能优化建议:")
        print("\n1. 硬件优化:")
        print("   - 确保有足够的RAM (推荐16GB+)")
        print("   - 使用SSD存储模型文件")
        print("   - 如有GPU，确保CUDA/ROCm驱动正确安装")
        
        print("\n2. 模型选择:")
        print("   - 7B模型在性能和质量间平衡较好")
        print("   - 考虑使用量化版本(Q4_K_M)减少内存占用")
        print("   - 避免同时加载多个大模型")
        
        print("\n3. 系统配置:")
        print("   - 关闭不必要的后台程序")
        print("   - 设置Ollama环境变量:")
        print("     export OLLAMA_NUM_PARALLEL=1")
        print("     export OLLAMA_MAX_LOADED_MODELS=1")
        print("     export OLLAMA_FLASH_ATTENTION=1")
        
        print("\n4. 请求优化:")
        print("   - 使用流式输出(stream=true)提升响应感知")
        print("   - 适当调整temperature和top_p参数")
        print("   - 控制max_tokens避免过长生成")
        
        print("\n5. 应用层优化:")
        print("   - 增大文本分块大小减少API调用")
        print("   - 使用连接池复用HTTP连接")
        print("   - 实现请求缓存机制")

def main():
    print("🔧 Ollama性能优化工具")
    print("=" * 50)
    
    optimizer = OllamaOptimizer()
    
    # 检查服务状态
    if not optimizer.check_ollama_status():
        print("请先启动Ollama服务: ollama serve")
        sys.exit(1)
    
    print("✅ Ollama服务运行正常")
    
    # 检查目标模型
    model_name = "qwen2.5:7b"
    model_info = optimizer.get_model_info(model_name)
    
    if not model_info:
        print(f"❌ 模型 {model_name} 未找到")
        print(f"请先下载模型: ollama pull {model_name}")
        sys.exit(1)
    
    print(f"✅ 找到模型 {model_name}")
    print(f"   大小: {model_info.get('size', 0) / (1024**3):.2f} GB")
    
    # 预加载模型
    if optimizer.preload_model(model_name):
        # 性能测试
        performance = optimizer.test_model_performance(model_name)
        
        if performance:
            # 性能评估
            tokens_per_second = performance.get('tokens_per_second', 0)
            if tokens_per_second > 10:
                print("🎉 模型性能良好!")
            elif tokens_per_second > 5:
                print("⚠️ 模型性能一般，建议优化")
            else:
                print("🐌 模型性能较慢，需要优化")
    
    # 输出优化建议
    optimizer.optimize_system_settings()
    
    print("\n✨ 优化完成! 现在可以重启招标文件生成服务以获得更好的性能。")

if __name__ == "__main__":
    main()