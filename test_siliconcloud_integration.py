#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SiliconCloud集成测试脚本

功能:
1. 测试SiliconCloud客户端初始化
2. 测试模型可用性检查
3. 测试模型调用功能
4. 测试模型切换功能

使用前请确保:
1. 已在config/model_config.json中配置了有效的SiliconCloud API密钥
2. 网络连接正常，能够访问api.siliconflow.cn
"""

import sys
import os
import json
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm_service.model_manager import ModelManager

def test_siliconcloud_integration():
    """
    测试SiliconCloud集成功能
    """
    print("=== SiliconCloud集成测试 ===")
    print()
    
    try:
        # 1. 初始化模型管理器
        print("1. 初始化模型管理器...")
        manager = ModelManager()
        print(f"✅ 模型管理器初始化成功")
        print(f"   可用客户端: {list(manager.clients.keys())}")
        print()
        
    
        # 2. 检查SiliconCloud配置
        print("2. 检查SiliconCloud配置...")
        config = manager.config
        siliconcloud_config = config.get('providers', {}).get('siliconcloud', {})
        
        if not siliconcloud_config:
            print("❌ SiliconCloud配置未找到")
            return False
            
        api_key = siliconcloud_config.get('api_key', '')
        if api_key == 'your_siliconcloud_api_key_here' or not api_key:
            print("❌ SiliconCloud API密钥未配置")
            print("   请在config/model_config.json中配置有效的API密钥")
            return False
            
        print(f"✅ SiliconCloud配置检查通过")
        print(f"   Base URL: {siliconcloud_config.get('base_url')}")
        print(f"   Model: {siliconcloud_config.get('model')}")
        print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
        print()
        
        # 3. 检查客户端初始化
        print("3. 检查SiliconCloud客户端初始化...")
        if 'siliconcloud' not in manager.clients:
            print("❌ SiliconCloud客户端未初始化")
            return False
        print("✅ SiliconCloud客户端初始化成功")
        print()
        
        # 4. 测试模型可用性
        print("4. 测试SiliconCloud模型可用性...")
        start_time = time.time()
        availability = manager.check_model_availability('siliconcloud')
        check_time = round((time.time() - start_time) * 1000, 2)
        
        print(f"   检查耗时: {check_time}ms")
        print(f"   可用性: {availability['available']}")
        print(f"   消息: {availability['message']}")
        
        if availability.get('response_time'):
            print(f"   响应时间: {availability['response_time']}ms")
            
        if not availability['available']:
            print("❌ SiliconCloud模型不可用")
            return False
        print("✅ SiliconCloud模型可用性检查通过")
        print()
        
        # 5. 测试简单模型调用
        print("5. 测试SiliconCloud模型调用...")
        test_prompt = "请简单介绍一下人工智能，限制在50字以内。"
        
        try:
            start_time = time.time()
            response = manager._call_siliconcloud(test_prompt)
            call_time = round((time.time() - start_time) * 1000, 2)
            
            print(f"✅ 模型调用成功")
            print(f"   调用耗时: {call_time}ms")
            print(f"   提示词: {test_prompt}")
            print(f"   响应: {response[:100]}{'...' if len(response) > 100 else ''}")
            print()
            
        except Exception as e:
            print(f"❌ 模型调用失败: {str(e)}")
            return False
        
        # 6. 测试通过模型管理器调用
        print("6. 测试通过模型管理器调用...")
        
        # 保存当前配置
        original_tender_notice = manager.get_current_model('tender_notice')
        original_tender_generation = manager.get_current_model('tender_generation')
        
        try:
            # 切换到SiliconCloud
            success1 = manager.set_current_model('tender_notice', 'siliconcloud')
            success2 = manager.set_current_model('tender_generation', 'siliconcloud')
            
            if not (success1 and success2):
                print("❌ 模型切换失败")
                return False
                
            print("✅ 模型切换成功")
            
            # 测试调用
            test_prompt = "请用一句话描述机器学习。"
            start_time = time.time()
            response = manager.call_model('tender_notice', test_prompt)
            call_time = round((time.time() - start_time) * 1000, 2)
            
            print(f"✅ 通过模型管理器调用成功")
            print(f"   调用耗时: {call_time}ms")
            print(f"   响应: {response[:100]}{'...' if len(response) > 100 else ''}")
            print()
            
        except Exception as e:
            print(f"❌ 通过模型管理器调用失败: {str(e)}")
            return False
        finally:
            # 恢复原始配置
            manager.set_current_model('tender_notice', original_tender_notice)
            manager.set_current_model('tender_generation', original_tender_generation)
            print(f"✅ 已恢复原始模型配置")
            print()
        
        # 7. 测试模型信息获取
        print("7. 测试模型信息获取...")
        model_info = manager.get_model_info()
        
        print("✅ 模型信息获取成功")
        print(f"   可用模块: {list(model_info['models'].keys())}")
        print(f"   可用提供商: {list(model_info['providers'].keys())}")
        
        # 检查SiliconCloud是否在选项中
        for module, config in model_info['models'].items():
            if 'siliconcloud' in config.get('options', []):
                print(f"   模块 {module} 支持SiliconCloud: ✅")
            else:
                print(f"   模块 {module} 支持SiliconCloud: ❌")
        print()
        
        print("=== 测试结果 ===")
        print("🎉 所有测试通过！SiliconCloud集成成功！")
        print()
        print("现在您可以：")
        print("1. 在Web界面中选择SiliconCloud作为模型提供商")
        print("2. 通过API切换到SiliconCloud模型")
        print("3. 使用SiliconCloud进行招标信息提取和招标书生成")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_configuration_guide():
    """
    显示配置指南
    """
    print("=== SiliconCloud配置指南 ===")
    print()
    print("如果测试失败，请按照以下步骤配置：")
    print()
    print("1. 获取SiliconCloud API密钥：")
    print("   - 访问 https://siliconflow.cn/")
    print("   - 注册账号并登录")
    print("   - 在控制台创建API密钥")
    print()
    print("2. 配置API密钥：")
    print("   - 编辑 config/model_config.json")
    print("   - 将 'your_siliconcloud_api_key_here' 替换为您的API密钥")
    print()
    print("3. 重新运行测试：")
    print("   python test_siliconcloud_integration.py")
    print()
    print("详细配置说明请参考：config/siliconcloud_config_example.md")
    print()

if __name__ == "__main__":
    print("SiliconCloud集成测试工具")
    print("=" * 50)
    print()
    
    success = test_siliconcloud_integration()
    
    if not success:
        print()
        show_configuration_guide()
        sys.exit(1)
    else:
        print("测试完成，SiliconCloud集成正常！")
        sys.exit(0)