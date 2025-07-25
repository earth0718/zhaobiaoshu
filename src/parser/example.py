#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档解析模块使用示例

演示如何使用文档解析模块的各种功能
"""

import json
import os
from pathlib import Path

from document_parser import DocumentParser, parse_document_to_json, extract_text_from_document
from document_service import DocumentService, get_document_service


def example_basic_parsing():
    """基础解析示例"""
    print("=== 基础文档解析示例 ===")
    
    # 创建解析器实例
    parser = DocumentParser()
    
    # 示例文件路径（请替换为实际文件路径）
    sample_files = [
        "sample.pdf",
        "sample.docx",
        "sample.txt"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            try:
                print(f"\n正在解析文件: {file_path}")
                
                # 解析文档
                result = parser.parse_to_json(file_path)
                
                print(f"解析成功！")
                print(f"文件名: {result['document_info']['filename']}")
                print(f"文件类型: {result['document_info']['file_type']}")
                print(f"元素数量: {result['document_info']['total_elements']}")
                
                # 保存结果到JSON文件
                output_file = f"{Path(file_path).stem}_parsed.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"结果已保存到: {output_file}")
                
            except Exception as e:
                print(f"解析失败: {str(e)}")
        else:
            print(f"文件不存在: {file_path}")


def example_text_extraction():
    """文本提取示例"""
    print("\n=== 文本提取示例 ===")
    
    sample_file = "sample.pdf"  # 请替换为实际文件路径
    
    if os.path.exists(sample_file):
        try:
            # 提取纯文本
            text = extract_text_from_document(sample_file)
            
            print(f"从 {sample_file} 提取的文本:")
            print(f"文本长度: {len(text)} 字符")
            print(f"前200字符: {text[:200]}...")
            
            # 保存文本到文件
            text_file = f"{Path(sample_file).stem}_text.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"文本已保存到: {text_file}")
            
        except Exception as e:
            print(f"文本提取失败: {str(e)}")
    else:
        print(f"文件不存在: {sample_file}")


def example_service_usage():
    """服务使用示例"""
    print("\n=== 文档服务使用示例 ===")
    
    # 获取服务实例
    service = get_document_service()
    
    # 检查支持的格式
    formats = service.get_supported_formats()
    print("支持的文件格式:")
    for ext, file_type in formats['format_mapping'].items():
        print(f"  {ext} -> {file_type}")
    
    # 验证文件
    test_files = ["test.pdf", "test.docx", "test.txt", "test.jpg"]
    print("\n文件格式验证:")
    for filename in test_files:
        validation = service.validate_file(filename)
        status = "✓" if validation['is_supported'] else "✗"
        print(f"  {status} {filename} ({validation['extension']})")


def example_structured_data_extraction():
    """结构化数据提取示例"""
    print("\n=== 结构化数据提取示例 ===")
    
    sample_file = "sample.pdf"  # 请替换为实际文件路径
    
    if os.path.exists(sample_file):
        try:
            # 读取文件内容
            with open(sample_file, 'rb') as f:
                file_content = f.read()
            
            service = get_document_service()
            
            # 提取特定类型的元素
            target_types = ['Title', 'Header', 'Table']
            result = service.extract_structured_data(
                file_content=file_content,
                filename=os.path.basename(sample_file),
                target_types=target_types
            )
            
            print(f"结构化数据提取结果:")
            print(f"总元素数: {result['document_info']['total_elements']}")
            print(f"元素类型: {result['document_info']['element_types']}")
            
            # 显示每种类型的元素数量
            for element_type, elements in result['structured_data'].items():
                print(f"  {element_type}: {len(elements)} 个")
            
            # 保存结构化数据
            output_file = f"{Path(sample_file).stem}_structured.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"结构化数据已保存到: {output_file}")
            
        except Exception as e:
            print(f"结构化数据提取失败: {str(e)}")
    else:
        print(f"文件不存在: {sample_file}")


def example_batch_processing():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")
    
    # 模拟文件数据
    sample_files = ["sample1.pdf", "sample2.docx", "sample3.txt"]
    
    # 准备文件数据（在实际使用中，这些应该是真实的文件内容）
    files_data = []
    for filename in sample_files:
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                content = f.read()
            files_data.append({
                'content': content,
                'filename': filename
            })
    
    if files_data:
        try:
            service = get_document_service()
            
            # 批量解析
            results = service.batch_parse_files(files_data)
            
            print(f"批量处理结果:")
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful
            print(f"总文件数: {len(results)}")
            print(f"成功: {successful}")
            print(f"失败: {failed}")
            
            # 显示详细结果
            for result in results:
                status = "✓" if result['success'] else "✗"
                filename = result['filename']
                if result['success']:
                    elements = result['data']['document_info']['total_elements']
                    print(f"  {status} {filename} - {elements} 个元素")
                else:
                    error = result['error']
                    print(f"  {status} {filename} - 错误: {error}")
            
        except Exception as e:
            print(f"批量处理失败: {str(e)}")
    else:
        print("没有找到可处理的文件")


def main():
    """主函数"""
    print("文档解析模块使用示例")
    print("=" * 50)
    
    # 运行各种示例
    example_basic_parsing()
    example_text_extraction()
    example_service_usage()
    example_structured_data_extraction()
    example_batch_processing()
    
    print("\n=== 示例运行完成 ===")
    print("\n注意事项:")
    print("1. 请确保已安装 unstructured 库及其依赖")
    print("2. 将示例中的文件路径替换为实际存在的文件")
    print("3. 对于PDF文件，可能需要安装额外的依赖（如 poppler）")
    print("4. 某些功能可能需要网络连接来下载模型")


if __name__ == "__main__":
    main()