@echo off
echo 启动优化的Ollama服务...

REM 设置Ollama性能优化环境变量
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_MAX_LOADED_MODELS=1
set OLLAMA_FLASH_ATTENTION=1
set OLLAMA_HOST=0.0.0.0:11434

REM 显示当前配置
echo ================================
echo Ollama性能优化配置:
echo OLLAMA_NUM_PARALLEL=%OLLAMA_NUM_PARALLEL%
echo OLLAMA_MAX_LOADED_MODELS=%OLLAMA_MAX_LOADED_MODELS%
echo OLLAMA_FLASH_ATTENTION=%OLLAMA_FLASH_ATTENTION%
echo OLLAMA_HOST=%OLLAMA_HOST%
echo ================================

REM 启动Ollama服务
echo 正在启动Ollama服务...
ollama serve

pause