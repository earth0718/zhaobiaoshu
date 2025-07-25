/**
 * 招标书生成页面组件
 * 提供文档上传、生成选项配置、进度跟踪和结果展示功能
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  Card,
  Row,
  Col,
  Form,
  Select,
  Button,
  Space,
  Alert,
  Divider,
  Typography,
  Progress,
  message,
  Tag,
  Steps,
} from 'antd';
import {
  RobotOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  ClearOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import FileUpload from '../common/FileUpload';
import LoadingSpinner from '../common/LoadingSpinner';
import ResultDisplay from '../common/ResultDisplay';
import { tenderService } from '../../services/apiService';
import { 
  QUALITY_LEVELS, 
  MODEL_PROVIDERS, 
  STATUS_MAP,
  API_CONFIG 
} from '../../config/apiConfig';

const { Title, Text } = Typography;
const { Step } = Steps;
const { Option } = Select;

const TenderGenerator = () => {
  const [form] = Form.useForm();
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [availableModels, setAvailableModels] = useState([]);
  const pollingRef = useRef(null);

  // 获取可用模型列表
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const models = await tenderService.getAvailableModels();
        setAvailableModels(models);
      } catch (error) {
        console.error('获取模型列表失败:', error);
      }
    };
    fetchModels();
  }, []);

  // 清理轮询
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  // 处理文件选择
  const handleFileSelect = useCallback((file) => {
    setSelectedFile(file);
    setResult(null);
    setTaskId(null);
    setProgress(0);
    setCurrentStep(0);
    message.info(`已选择文件: ${file.name}`);
  }, []);

  // 处理文件移除
  const handleFileRemove = useCallback(() => {
    setSelectedFile(null);
    setResult(null);
    setTaskId(null);
    setProgress(0);
    setCurrentStep(0);
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }
    message.info('已移除文件');
  }, []);

  // 轮询任务状态
  const pollTaskStatus = useCallback(async (id) => {
    let attempts = 0;
    const maxAttempts = API_CONFIG.POLLING.MAX_ATTEMPTS;
    
    pollingRef.current = setInterval(async () => {
      try {
        attempts++;
        const status = await tenderService.getTaskStatus(id);
        
        // 更新进度
        setProgress(status.progress || 0);
        
        // 更新步骤
        switch (status.status) {
          case STATUS_MAP.PENDING:
            setCurrentStep(0);
            break;
          case STATUS_MAP.PROCESSING:
            setCurrentStep(1);
            break;
          case STATUS_MAP.COMPLETED:
            setCurrentStep(2);
            break;
          case STATUS_MAP.FAILED:
            setCurrentStep(3);
            break;
        }

        if (status.status === STATUS_MAP.COMPLETED) {
          setResult(status.result);
          setLoading(false);
          setProgress(100);
          clearInterval(pollingRef.current);
          message.success('招标书生成完成！');
        } else if (status.status === STATUS_MAP.FAILED) {
          setLoading(false);
          clearInterval(pollingRef.current);
          message.error(`生成失败: ${status.message}`);
        }

        // 超时处理
        if (attempts >= maxAttempts) {
          setLoading(false);
          clearInterval(pollingRef.current);
          message.warning('任务处理时间较长，请稍后手动查询结果');
        }
      } catch (error) {
        console.error('查询任务状态失败:', error);
        attempts++;
        if (attempts >= 3) {
          setLoading(false);
          clearInterval(pollingRef.current);
          message.error('无法获取任务状态，请稍后重试');
        }
      }
    }, API_CONFIG.POLLING.INTERVAL);
  }, []);

  // 执行招标书生成
  const handleGenerate = useCallback(async () => {
    if (!selectedFile) {
      message.warning('请先选择要处理的文件');
      return;
    }

    try {
      setLoading(true);
      setResult(null);
      setProgress(0);
      setCurrentStep(0);

      const formValues = form.getFieldsValue();
      const generateResult = await tenderService.generateTender(selectedFile, {
        model_provider: formValues.model_provider,
        quality_level: formValues.quality_level,
      });

      setTaskId(generateResult.task_id);
      setCurrentStep(1);
      message.success('任务已创建，正在生成招标书...');
      
      // 开始轮询任务状态
      pollTaskStatus(generateResult.task_id);
    } catch (error) {
      console.error('生成失败:', error);
      message.error(`生成失败: ${error.message}`);
      setLoading(false);
      setCurrentStep(3);
    }
  }, [selectedFile, form, pollTaskStatus]);

  // 清除所有内容
  const handleClear = useCallback(() => {
    setSelectedFile(null);
    setResult(null);
    setTaskId(null);
    setProgress(0);
    setCurrentStep(0);
    form.resetFields();
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }
    setLoading(false);
    message.info('已清除所有内容');
  }, [form]);

  // 渲染进度步骤
  const renderProgressSteps = () => {
    const steps = [
      {
        title: '准备中',
        description: '等待处理',
        icon: <ClockCircleOutlined />,
      },
      {
        title: '生成中',
        description: 'AI正在生成招标书',
        icon: <RobotOutlined />,
      },
      {
        title: '完成',
        description: '招标书生成完成',
        icon: <CheckCircleOutlined />,
      },
      {
        title: '失败',
        description: '生成过程出现错误',
        icon: <ExclamationCircleOutlined />,
        status: 'error',
      },
    ];

    return (
      <Steps current={currentStep} size="small">
        {steps.map((step, index) => (
          <Step
            key={index}
            title={step.title}
            description={step.description}
            icon={step.icon}
            status={index === 3 && currentStep === 3 ? 'error' : undefined}
          />
        ))}
      </Steps>
    );
  };

  return (
    <div className="tender-generator">
      <Title level={2}>
        <RobotOutlined /> 招标书生成
      </Title>
      <Text type="secondary">
        基于AI技术，从您的文档中智能生成专业的招标书，支持多种质量级别和模型选择
      </Text>

      <Divider />

      <Row gutter={[24, 24]}>
        {/* 左侧：文件上传和配置 */}
        <Col xs={24} lg={12}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {/* 文件上传 */}
            <Card title="文档上传" size="small">
              <FileUpload
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
                accept=".pdf,.docx,.doc"
                uploadText="选择要生成招标书的文档"
                uploadHint="支持PDF、Word格式，建议文档内容完整清晰"
              />
            </Card>

            {/* 生成配置 */}
            <Card
              title={
                <Space>
                  <SettingOutlined />
                  <span>生成配置</span>
                </Space>
              }
              size="small"
            >
              <Form form={form} layout="vertical">
                <Form.Item
                  name="model_provider"
                  label="模型提供商"
                  initialValue="ollama"
                  rules={[{ required: true, message: '请选择模型提供商' }]}
                >
                  <Select placeholder="选择模型提供商">
                    {MODEL_PROVIDERS.map(provider => (
                      <Option key={provider.value} value={provider.value}>
                        <Space direction="vertical" size={0}>
                          <Text strong>{provider.label}</Text>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {provider.description}
                          </Text>
                        </Space>
                      </Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  name="quality_level"
                  label="生成质量"
                  initialValue="standard"
                  rules={[{ required: true, message: '请选择生成质量' }]}
                >
                  <Select placeholder="选择生成质量">
                    {QUALITY_LEVELS.map(level => (
                      <Option key={level.value} value={level.value}>
                        <Space direction="vertical" size={0}>
                          <Text strong>{level.label}</Text>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {level.description}
                          </Text>
                        </Space>
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Form>
            </Card>

            {/* 操作按钮 */}
            <Card size="small">
              <Space style={{ width: '100%', justifyContent: 'center' }}>
                <Button
                  type="primary"
                  size="large"
                  icon={<PlayCircleOutlined />}
                  onClick={handleGenerate}
                  disabled={!selectedFile || loading}
                  loading={loading}
                >
                  生成招标书
                </Button>
                <Button
                  icon={<ClearOutlined />}
                  onClick={handleClear}
                  disabled={loading}
                >
                  清除
                </Button>
              </Space>
            </Card>

            {/* 进度显示 */}
            {(loading || taskId) && (
              <Card title="生成进度" size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  {renderProgressSteps()}
                  {loading && (
                    <Progress
                      percent={progress}
                      status={currentStep === 3 ? 'exception' : 'active'}
                      strokeColor={{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                      }}
                    />
                  )}
                  {taskId && (
                    <Text type="secondary">
                      任务ID: <Text code>{taskId}</Text>
                    </Text>
                  )}
                </Space>
              </Card>
            )}
          </Space>
        </Col>

        {/* 右侧：结果展示 */}
        <Col xs={24} lg={12}>
          <Card title="生成结果" size="small" style={{ minHeight: '600px' }}>
            {loading ? (
              <LoadingSpinner
                loading={true}
                type="tender"
                tip="正在生成招标书..."
                description="AI正在为您生成专业的招标书文档"
                progress={progress}
              />
            ) : result ? (
              <ResultDisplay
                result={result}
                type="tender"
                title="招标书生成结果"
                showMetadata={true}
                showActions={true}
              />
            ) : (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '400px',
                color: '#999'
              }}>
                <Space direction="vertical" style={{ textAlign: 'center' }}>
                  <RobotOutlined style={{ fontSize: '48px' }} />
                  <Text type="secondary">上传文档并点击"生成招标书"开始</Text>
                </Space>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 使用说明 */}
      <Divider />
      <Alert
        message="使用说明"
        description={
          <ul style={{ marginBottom: 0, paddingLeft: '20px' }}>
            <li><strong>文档要求</strong>：支持PDF、Word格式，建议文档内容完整、结构清晰</li>
            <li><strong>模型选择</strong>：Ollama本地模型数据安全，DeepSeek云端模型性能更强</li>
            <li><strong>质量级别</strong>：基础质量速度快，标准质量平衡，高级质量最佳但耗时较长</li>
            <li><strong>生成时间</strong>：根据文档大小和质量级别，通常需要2-10分钟</li>
            <li><strong>结果格式</strong>：生成的招标书采用Markdown格式，可直接下载或复制使用</li>
          </ul>
        }
        type="info"
        showIcon
      />
    </div>
  );
};

export default TenderGenerator;