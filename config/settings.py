import os

# 在现有的 Config 类中添加日志配置
import logging

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # 文件上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Ollama配置
    OLLAMA_URL = os.environ.get('OLLAMA_URL') or 'http://localhost:11434'
    MODEL_NAME = os.environ.get('MODEL_NAME') or 'qwen2.5:7b'
    
    # Embedding模型配置
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL') or 'mxbai-embed-large:latest'
    
    # 日志配置
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs('templates_repo', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=Config.LOG_LEVEL,
            format=Config.LOG_FORMAT,
            handlers=[
                logging.FileHandler('logs/app.log'),
                logging.StreamHandler()
            ]
        )
        
        # 确保日志目录存在
        os.makedirs('logs', exist_ok=True)