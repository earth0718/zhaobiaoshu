#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用Ollama速度优化配置
将速度优化配置应用到主配置文件
"""

import shutil
import os
from pathlib import Path

def apply_speed_config():
    """应用速度优化配置"""
    config_dir = Path("config")
    
    # 备份原配置
    original_config = config_dir / "tender_generation_config.ini"
    backup_config = config_dir / "tender_generation_config.ini.backup"
    speed_config = config_dir / "ollama_speed_config.ini"
    
    if not speed_config.exists():
        print("❌ 速度优化配置文件不存在")
        return False
    
    try:
        # 备份原配置
        if original_config.exists():
            shutil.copy2(original_config, backup_config)
            print(f"✅ 已备份原配置到: {backup_config}")
        
        # 应用速度配置
        shutil.copy2(speed_config, original_config)
        print(f"✅ 已应用速度优化配置")
        
        print("\n🚀 Ollama速度优化配置已生效!")
        print("\n主要优化项目:")
        print("  ✓ 增大文本分块大小 (5000 tokens)")
        print("  ✓ 减少重叠区域 (50 tokens)")
        print("  ✓ 优化模型参数 (temperature=0.6, top_p=0.8)")
        print("  ✓ 限制生成长度 (1500 tokens)")
        print("  ✓ 启用流式输出")
        print("  ✓ 精简招标书章节")
        print("  ✓ 使用基础质量级别")
        print("  ✓ 减少并行线程数")
        
        print("\n📝 使用建议:")
        print("  1. 重启后端服务以应用新配置")
        print("  2. 使用较小的文档进行测试")
        print("  3. 如需恢复原配置，运行: python restore_config.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 应用配置失败: {e}")
        return False

def restore_original_config():
    """恢复原始配置"""
    config_dir = Path("config")
    original_config = config_dir / "tender_generation_config.ini"
    backup_config = config_dir / "tender_generation_config.ini.backup"
    
    if not backup_config.exists():
        print("❌ 备份配置文件不存在")
        return False
    
    try:
        shutil.copy2(backup_config, original_config)
        print("✅ 已恢复原始配置")
        return True
    except Exception as e:
        print(f"❌ 恢复配置失败: {e}")
        return False

def main():
    print("🔧 Ollama速度优化配置工具")
    print("=" * 40)
    
    choice = input("请选择操作:\n1. 应用速度优化配置\n2. 恢复原始配置\n请输入选择 (1/2): ").strip()
    
    if choice == "1":
        apply_speed_config()
    elif choice == "2":
        restore_original_config()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()