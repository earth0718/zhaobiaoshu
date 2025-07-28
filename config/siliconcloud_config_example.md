# SiliconCloud（硅基流动）配置说明

## 概述

SiliconCloud（硅基流动）是一个提供大语言模型API服务的平台，支持多种开源和商业化模型。本项目已集成SiliconCloud作为第三种大模型调用方式。

## 配置步骤

### 1. 获取API密钥

1. 访问 [SiliconCloud官网](https://siliconflow.cn/)
2. 注册账号并登录
3. 进入控制台，创建API密钥
4. 复制生成的API密钥

### 2. 配置API密钥

编辑 `config/model_config.json` 文件，将 `your_siliconcloud_api_key_here` 替换为您的实际API密钥：

```json
{
  "providers": {
    "siliconcloud": {
      "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxx",
      "base_url": "https://api.siliconflow.cn/v1",
      "model": "Qwen/Qwen2.5-7B-Instruct"
    }
  }
}
```

### 3. 可用模型

SiliconCloud支持多种模型，您可以根据需要修改 `model` 字段：

- `Qwen/Qwen2.5-7B-Instruct` - 通义千问2.5 7B指令模型（推荐）
- `Qwen/Qwen2.5-14B-Instruct` - 通义千问2.5 14B指令模型
- `Qwen/Qwen2.5-32B-Instruct` - 通义千问2.5 32B指令模型
- `meta-llama/Llama-3.1-8B-Instruct` - Llama 3.1 8B指令模型
- `meta-llama/Llama-3.1-70B-Instruct` - Llama 3.1 70B指令模型
- `deepseek-ai/DeepSeek-V2.5` - DeepSeek V2.5模型

### 4. 切换到SiliconCloud

配置完成后，您可以通过以下方式切换模型：

#### 方法1：修改配置文件

编辑 `config/model_config.json`，将对应模块的 `current` 字段设置为 `siliconcloud`：

```json
{
  "models": {
    "tender_notice": {
      "current": "siliconcloud",
      "options": ["ollama", "deepseek", "siliconcloud"]
    },
    "tender_generation": {
      "current": "siliconcloud",
      "options": ["ollama", "deepseek", "siliconcloud"]
    }
  }
}
```

#### 方法2：通过API切换（如果有管理界面）

使用模型管理API动态切换模型提供商。

## 使用说明

### 优势

- **高性能**：基于优化的推理引擎，响应速度快
- **多模型支持**：支持多种开源和商业化模型
- **稳定可靠**：专业的云服务，高可用性
- **成本效益**：相比其他商业API，价格更具竞争力

### 注意事项

1. **API密钥安全**：请妥善保管您的API密钥，不要泄露给他人
2. **使用限制**：根据您的账户类型，可能存在调用频率和额度限制
3. **网络连接**：确保服务器能够访问 `api.siliconflow.cn`
4. **模型选择**：不同模型的性能和成本不同，请根据实际需求选择

### 故障排除

#### 常见错误

1. **401 Unauthorized**
   - 检查API密钥是否正确配置
   - 确认API密钥是否有效且未过期

2. **403 Forbidden**
   - 检查账户余额是否充足
   - 确认是否超出调用频率限制

3. **404 Not Found**
   - 检查模型名称是否正确
   - 确认所选模型是否在您的账户权限范围内

4. **连接超时**
   - 检查网络连接
   - 确认防火墙设置是否阻止了API访问

#### 调试方法

1. 查看日志文件，了解详细错误信息
2. 使用模型可用性检查功能测试连接
3. 尝试使用其他模型进行对比测试

## 技术支持

如果遇到问题，可以：

1. 查看SiliconCloud官方文档
2. 联系SiliconCloud技术支持
3. 在项目GitHub仓库提交Issue

## 更新日志

- 2024-01-28: 初始版本，支持基本的模型调用功能
- 支持的功能：
  - 招标信息提取
  - 招标书生成
  - 模型可用性检查
  - 动态模型切换