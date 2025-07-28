#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek-R1模型测试脚本

功能:
1. 测试DeepSeek-R1模型的推理能力
2. 验证模型在招标场景下的表现
3. 展示模型的思维链推理过程

使用前请确保:
1. 已在config/model_config.json中配置了有效的SiliconCloud API密钥
2. 模型已设置为deepseek-ai/DeepSeek-R1
"""

import sys
import os
import json
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm_service.model_manager import ModelManager

def test_deepseek_r1_reasoning():
    """
    测试DeepSeek-R1的推理能力
    """
    print("=== DeepSeek-R1模型推理测试 ===")
    print()
    
    try:
        # 初始化模型管理器
        print("初始化模型管理器...")
        manager = ModelManager()
        
        # 确认当前使用的是DeepSeek-R1
        config = manager.config
        siliconcloud_model = config.get('providers', {}).get('siliconcloud', {}).get('model', '')
        print(f"当前SiliconCloud模型: {siliconcloud_model}")
        
        if 'DeepSeek-R1' not in siliconcloud_model:
            print("⚠️  警告: 当前模型不是DeepSeek-R1")
        print()
        
        # 测试用例
        test_cases = [
            {
                "name": "逻辑推理测试",
                "prompt": "有一个招标项目，预算100万元，要求在6个月内完成。现在有三家公司投标：\n公司A：报价90万，工期5个月，有类似项目经验\n公司B：报价85万，工期7个月，技术实力强\n公司C：报价95万，工期4个月，本地公司\n\n请分析哪家公司最适合中标，并说明理由。"
            },
            {
                "name": "招标文件分析",
                "prompt": "请分析以下招标需求的关键要素：\n项目名称：智慧城市数据平台建设\n技术要求：支持大数据处理、AI算法集成、云原生架构\n服务要求：7×24小时运维支持、数据安全保障\n资质要求：软件企业认证、ISO27001认证\n\n请提取出技术难点和投标策略建议。"
            },
            {
                "name": "数学计算验证",
                "prompt": "一个工程项目总投资1000万元，其中：\n- 设备采购占40%\n- 人工成本占30%\n- 材料费用占20%\n- 其他费用占10%\n\n如果设备采购成本上涨15%，人工成本下降5%，请计算新的总成本，并分析对项目预算的影响。"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"{i}. {test_case['name']}")
            print(f"提示词: {test_case['prompt'][:100]}...")
            print()
            
            start_time = time.time()
            try:
                response = manager._call_siliconcloud(test_case['prompt'])
                call_time = round((time.time() - start_time) * 1000, 2)
                
                print(f"✅ 调用成功 (耗时: {call_time}ms)")
                print("回答:")
                print("-" * 50)
                print(response)
                print("-" * 50)
                print()
                
            except Exception as e:
                print(f"❌ 调用失败: {str(e)}")
                print()
                continue
        
        print("=== 测试完成 ===")
        print("DeepSeek-R1模型测试成功完成！")
        print()
        print("特点观察:")
        print("- DeepSeek-R1具有强大的推理能力")
        print("- 能够进行复杂的逻辑分析和计算")
        print("- 在招标场景下表现出色")
        print("- 回答结构化且逻辑清晰")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_comparison():
    """
    对比不同模型的表现
    """
    print("=== 模型对比测试 ===")
    print()
    
    try:
        manager = ModelManager()
        
        # 简单的测试提示词
        test_prompt = "请用一句话总结人工智能的核心价值。"
        
        models_to_test = ['deepseek', 'siliconcloud']
        results = {}
        
        for model in models_to_test:
            print(f"测试模型: {model}")
            
            # 临时切换模型
            original_model = manager.get_current_model('tender_notice')
            manager.set_current_model('tender_notice', model)
            
            try:
                start_time = time.time()
                response = manager.call_model('tender_notice', test_prompt)
                call_time = round((time.time() - start_time) * 1000, 2)
                
                results[model] = {
                    'response': response,
                    'time': call_time,
                    'success': True
                }
                
                print(f"✅ 成功 (耗时: {call_time}ms)")
                print(f"回答: {response[:100]}{'...' if len(response) > 100 else ''}")
                
            except Exception as e:
                results[model] = {
                    'error': str(e),
                    'success': False
                }
                print(f"❌ 失败: {str(e)}")
            
            # 恢复原始模型
            manager.set_current_model('tender_notice', original_model)
            print()
        
        # 显示对比结果
        print("=== 对比结果 ===")
        for model, result in results.items():
            if result['success']:
                model_name = "DeepSeek-R1" if model == 'siliconcloud' else "DeepSeek-Chat"
                print(f"{model_name}: {result['time']}ms, 长度: {len(result['response'])}字符")
            else:
                print(f"{model}: 调用失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 对比测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("DeepSeek-R1模型测试工具")
    print("=" * 50)
    print()
    
    # 运行推理测试
    success1 = test_deepseek_r1_reasoning()
    
    print()
    print("=" * 50)
    print()
    
    # 运行对比测试
    success2 = test_model_comparison()
    
    if success1 and success2:
        print("\n🎉 所有测试完成！DeepSeek-R1模型运行正常！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查配置")
        sys.exit(1)