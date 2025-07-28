#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试下载功能修复
验证后端返回文件名而不是完整路径，以及前端能正确构建下载URL
"""

import requests
import json
import time
import os

def test_download_functionality():
    """测试下载功能修复"""
    base_url = "http://localhost:8000"
    
    # 创建测试用的招标文件JSON数据（修正格式以匹配section_manager.py的期望）
    test_data = {
        "content": [
            {
                "text": "项目名称：测试项目下载功能修复。这是一个用于测试下载功能修复的测试项目。",
                "section": "项目概述",
                "type": "project_info"
            },
            {
                "text": "技术要求1：系统应具备高可用性。系统需要保证99.9%的可用性，支持故障自动切换。",
                "section": "技术要求",
                "type": "technical"
            },
            {
                "text": "技术要求2：系统应支持大并发访问。系统需要支持至少1000个并发用户同时访问。",
                "section": "技术要求",
                "type": "technical"
            },
            {
                "text": "技术要求3：系统应具备良好的扩展性。系统架构应支持水平扩展和垂直扩展。",
                "section": "技术要求",
                "type": "technical"
            },
            {
                "text": "服务要求1：提供7x24小时技术支持。投标人应提供全天候的技术支持服务。",
                "section": "服务要求",
                "type": "service"
            },
            {
                "text": "服务要求2：提供完整的培训服务。包括系统操作培训和管理员培训。",
                "section": "服务要求",
                "type": "service"
            },
            {
                "text": "服务要求3：提供定期的系统维护。每月至少进行一次系统维护和优化。",
                "section": "服务要求",
                "type": "service"
            },
            {
                "text": "资质要求1：具备软件开发资质。投标人应具备软件企业认定证书。",
                "section": "资质要求",
                "type": "qualification"
            },
            {
                "text": "资质要求2：具备系统集成资质。投标人应具备信息系统集成及服务资质。",
                "section": "资质要求",
                "type": "qualification"
            },
            {
                "text": "资质要求3：具备相关行业经验。投标人应具备3年以上相关项目实施经验。",
                "section": "资质要求",
                "type": "qualification"
            }
        ],
        "metadata": {
            "tender_number": "TEST-2025-001",
            "tender_name": "下载功能修复测试项目",
            "budget": "100万元",
            "deadline": "2025-08-15"
        }
    }
    
    print("=== 测试下载功能修复 ===")
    print(f"测试数据: {test_data['metadata']['tender_name']}")
    
    try:
        # 1. 上传JSON文件并生成投标书
        print("\n1. 上传JSON文件并生成投标书...")
        
        # 将测试数据保存为临时JSON文件
        temp_json_file = "temp_test_download.json"
        with open(temp_json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 上传文件
        with open(temp_json_file, 'rb') as f:
            files = {'file': ('test_download.json', f, 'application/json')}
            data = {
                'model_name': 'qwen2.5:7b',
                'batch_size': 3,
                'generate_outline_only': False
            }
            
            response = requests.post(
                f"{base_url}/api/gender_book/upload_json",
                files=files,
                data=data
            )
        
        # 清理临时文件
        if os.path.exists(temp_json_file):
            os.remove(temp_json_file)
        
        if response.status_code != 200:
            print(f"❌ 上传失败: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"❌ 生成任务创建失败: {result.get('message', '未知错误')}")
            return False
        
        task_id = result.get('task_id')
        print(f"✅ 任务创建成功，任务ID: {task_id}")
        
        # 2. 轮询任务状态直到完成
        print("\n2. 等待任务完成...")
        max_wait_time = 300  # 最大等待5分钟
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status_response = requests.get(f"{base_url}/api/gender_book/status/{task_id}")
            
            if status_response.status_code != 200:
                print(f"❌ 获取任务状态失败: {status_response.status_code}")
                return False
            
            status_data = status_response.json()
            task_status = status_data.get('status')
            progress = status_data.get('progress', 0)
            message = status_data.get('message', '')
            
            print(f"   状态: {task_status}, 进度: {progress}%, 消息: {message}")
            
            if task_status == 'completed':
                print("✅ 任务完成！")
                result_data = status_data.get('result', {})
                
                # 3. 检查返回的文件名字段
                print("\n3. 检查返回的文件名字段...")
                word_filename = result_data.get('word_filename')
                markdown_filename = result_data.get('markdown_filename')
                
                print(f"   Word文件名: {word_filename}")
                print(f"   Markdown文件名: {markdown_filename}")
                
                # 验证返回的是文件名而不是完整路径
                if word_filename:
                    if '\\' in word_filename or '/' in word_filename:
                        print(f"❌ Word文件名包含路径分隔符，应该只是文件名: {word_filename}")
                        return False
                    else:
                        print(f"✅ Word文件名格式正确: {word_filename}")
                
                if markdown_filename:
                    if '\\' in markdown_filename or '/' in markdown_filename:
                        print(f"❌ Markdown文件名包含路径分隔符，应该只是文件名: {markdown_filename}")
                        return False
                    else:
                        print(f"✅ Markdown文件名格式正确: {markdown_filename}")
                
                # 4. 测试下载API端点
                print("\n4. 测试下载API端点...")
                
                if word_filename:
                    print(f"   测试Word文件下载: {word_filename}")
                    download_url = f"{base_url}/api/gender_book/download/word/{word_filename}"
                    download_response = requests.get(download_url)
                    
                    if download_response.status_code == 200:
                        print(f"✅ Word文件下载成功，文件大小: {len(download_response.content)} 字节")
                        
                        # 检查Content-Disposition头
                        content_disposition = download_response.headers.get('content-disposition', '')
                        if 'attachment' in content_disposition:
                            print(f"✅ Content-Disposition头正确: {content_disposition}")
                        else:
                            print(f"⚠️  Content-Disposition头可能不正确: {content_disposition}")
                    else:
                        print(f"❌ Word文件下载失败: {download_response.status_code} - {download_response.text}")
                        return False
                
                if markdown_filename:
                    print(f"   测试Markdown文件下载: {markdown_filename}")
                    download_url = f"{base_url}/api/gender_book/download/markdown/{markdown_filename}"
                    download_response = requests.get(download_url)
                    
                    if download_response.status_code == 200:
                        print(f"✅ Markdown文件下载成功，文件大小: {len(download_response.content)} 字节")
                        
                        # 检查Content-Disposition头
                        content_disposition = download_response.headers.get('content-disposition', '')
                        if 'attachment' in content_disposition:
                            print(f"✅ Content-Disposition头正确: {content_disposition}")
                        else:
                            print(f"⚠️  Content-Disposition头可能不正确: {content_disposition}")
                    else:
                        print(f"❌ Markdown文件下载失败: {download_response.status_code} - {download_response.text}")
                        return False
                
                print("\n=== 测试结果 ===")
                print("✅ 下载功能修复测试通过！")
                print("✅ 后端正确返回文件名而不是完整路径")
                print("✅ 下载API端点工作正常")
                print("✅ 前端应该能够正确构建下载URL")
                
                return True
                
            elif task_status == 'failed':
                error = status_data.get('error', '未知错误')
                print(f"❌ 任务失败: {error}")
                return False
            
            time.sleep(5)  # 等待5秒后再次检查
        
        print(f"❌ 任务超时，等待时间超过{max_wait_time}秒")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_download_functionality()
    if success:
        print("\n🎉 所有测试通过！下载功能修复成功。")
    else:
        print("\n💥 测试失败，请检查修复代码。")