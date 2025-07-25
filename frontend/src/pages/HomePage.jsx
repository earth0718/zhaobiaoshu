/**
 * 首页组件
 * 提供系统概览、快速入口和功能介绍
 */

import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Card,
  Typography,
  Button,
  Space,
  Statistic,
  Timeline,
  Alert,
  Divider,
  Tag,
  Progress,
} from 'antd';
import {
  FileTextOutlined,
  RobotOutlined,
  UnorderedListOutlined,
  CloudUploadOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  RightOutlined,
  ApiOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  GlobalOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { documentService, tenderService } from '../services/apiService';
import { API_CONFIG } from '../config/apiConfig';

const { Title, Paragraph, Text } = Typography;
const { Meta } = Card;

const HomePage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalTasks: 0,
    completedTasks: 0,
    runningTasks: 0,
    failedTasks: 0,
  });
  const [systemInfo, setSystemInfo] = useState({
    documentService: 'checking',
    tenderService: 'checking',
    supportedFormats: [],
    modelProviders: [],
  });
  const [loading, setLoading] = useState(true);

  // 获取系统信息和统计数据
  useEffect(() => {
    const fetchSystemInfo = async () => {
      try {
        setLoading(true);
        
        // 检查文档服务状态
        try {
          await documentService.checkHealth();
          const formats = await documentService.getSupportedFormats();
          setSystemInfo(prev => ({
            ...prev,
            documentService: 'online',
            supportedFormats: formats.data || [],
          }));
        } catch (error) {
          setSystemInfo(prev => ({ ...prev, documentService: 'offline' }));
        }

        // 检查招标服务状态
        try {
          await tenderService.checkHealth();
          const models = await tenderService.getModels();
          setSystemInfo(prev => ({
            ...prev,
            tenderService: 'online',
            modelProviders: models.data?.available_models || [],
          }));
        } catch (error) {
          setSystemInfo(prev => ({ ...prev, tenderService: 'offline' }));
        }

        // 获取任务统计（模拟数据，实际应该从API获取）
        setStats({
          totalTasks: 156,
          completedTasks: 142,
          runningTasks: 3,
          failedTasks: 11,
        });
      } catch (error) {
        console.error('获取系统信息失败:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSystemInfo();
  }, []);

  // 功能卡片配置
  const featureCards = [
    {
      key: 'document',
      title: '文档解析',
      description: '支持PDF、Word、TXT、MD等多种格式的文档解析，提取文本和结构化数据',
      icon: <FileTextOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      path: '/document',
      features: ['多格式支持', '文本提取', '结构化解析', '批量处理'],
      status: systemInfo.documentService,
    },
    {
      key: 'tender',
      title: '招标书生成',
      description: '基于AI技术，自动分析文档内容并生成专业的招标书文档',
      icon: <RobotOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      path: '/tender',
      features: ['AI生成', '多模型支持', '质量控制', '实时进度'],
      status: systemInfo.tenderService,
    },
    {
      key: 'tasks',
      title: '任务管理',
      description: '查看和管理所有文档处理任务，监控任务状态和下载结果',
      icon: <UnorderedListOutlined style={{ fontSize: '32px', color: '#fa8c16' }} />,
      path: '/tasks',
      features: ['状态监控', '结果下载', '历史记录', '批量操作'],
      status: 'online',
    },
  ];

  // 渲染状态标签
  const renderStatusTag = (status) => {
    const statusConfig = {
      online: { color: 'success', text: '在线' },
      offline: { color: 'error', text: '离线' },
      checking: { color: 'processing', text: '检查中' },
    };
    const config = statusConfig[status] || statusConfig.checking;
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 渲染功能卡片
  const renderFeatureCard = (card) => (
    <Card
      key={card.key}
      hoverable
      style={{ height: '100%' }}
      actions={[
        <Button
          type="primary"
          icon={<RightOutlined />}
          onClick={() => navigate(card.path)}
          disabled={card.status === 'offline'}
        >
          立即使用
        </Button>,
      ]}
    >
      <Meta
        avatar={card.icon}
        title={
          <Space>
            {card.title}
            {renderStatusTag(card.status)}
          </Space>
        }
        description={
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Paragraph style={{ margin: 0 }}>{card.description}</Paragraph>
            <Space wrap>
              {card.features.map(feature => (
                <Tag key={feature} color="blue">{feature}</Tag>
              ))}
            </Space>
          </Space>
        }
      />
    </Card>
  );

  // 系统特性
  const systemFeatures = [
    {
      icon: <ThunderboltOutlined style={{ color: '#faad14' }} />,
      title: '高性能处理',
      description: '采用异步处理架构，支持大文件和批量处理',
    },
    {
      icon: <SafetyCertificateOutlined style={{ color: '#52c41a' }} />,
      title: '安全可靠',
      description: '文件加密传输，处理完成后自动清理临时文件',
    },
    {
      icon: <GlobalOutlined style={{ color: '#1890ff' }} />,
      title: '多模型支持',
      description: '支持多种AI模型，可根据需求选择最适合的模型',
    },
    {
      icon: <ApiOutlined style={{ color: '#722ed1' }} />,
      title: 'RESTful API',
      description: '提供完整的API接口，支持第三方系统集成',
    },
  ];

  return (
    <div>
      {/* 欢迎区域 */}
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card>
            <Row align="middle">
              <Col flex="auto">
                <Space direction="vertical" size="small">
                  <Title level={2} style={{ margin: 0 }}>
                    欢迎使用招标书文档解析系统
                  </Title>
                  <Paragraph style={{ margin: 0, fontSize: '16px' }}>
                    基于AI技术的智能文档处理平台，支持多种格式文档解析和招标书自动生成
                  </Paragraph>
                </Space>
              </Col>
              <Col>
                <Button
                  type="primary"
                  size="large"
                  icon={<CloudUploadOutlined />}
                  onClick={() => navigate('/document')}
                >
                  开始使用
                </Button>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 统计数据 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={stats.totalTasks}
              prefix={<UnorderedListOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completedTasks}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="进行中"
              value={stats.runningTasks}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="失败"
              value={stats.failedTasks}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
            <Progress
              percent={Math.round((stats.failedTasks / stats.totalTasks) * 100)}
              size="small"
              status="exception"
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 主要功能 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Title level={3}>主要功能</Title>
        </Col>
        {featureCards.map(card => (
          <Col key={card.key} xs={24} md={8}>
            {renderFeatureCard(card)}
          </Col>
        ))}
      </Row>

      {/* 系统信息 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="系统状态" loading={loading}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Row justify="space-between">
                <Text>文档解析服务:</Text>
                {renderStatusTag(systemInfo.documentService)}
              </Row>
              <Row justify="space-between">
                <Text>招标生成服务:</Text>
                {renderStatusTag(systemInfo.tenderService)}
              </Row>
              <Divider style={{ margin: '12px 0' }} />
              <Text strong>支持的文件格式:</Text>
              <Space wrap>
                {systemInfo.supportedFormats.map(format => (
                  <Tag key={format}>{format.toUpperCase()}</Tag>
                ))}
              </Space>
              <Text strong>可用模型:</Text>
              <Space wrap>
                {systemInfo.modelProviders.map(model => (
                  <Tag key={model} color="green">{model}</Tag>
                ))}
              </Space>
            </Space>
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="系统特性">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              {systemFeatures.map((feature, index) => (
                <Row key={index} align="top" gutter={12}>
                  <Col flex="none">
                    {feature.icon}
                  </Col>
                  <Col flex="auto">
                    <Space direction="vertical" size={0}>
                      <Text strong>{feature.title}</Text>
                      <Text type="secondary">{feature.description}</Text>
                    </Space>
                  </Col>
                </Row>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 使用流程 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="使用流程">
            <Timeline
              items={[
                {
                  dot: <FileTextOutlined style={{ color: '#1890ff' }} />,
                  children: (
                    <Space direction="vertical" size={0}>
                      <Text strong>上传文档</Text>
                      <Text type="secondary">支持PDF、Word、TXT、MD等格式</Text>
                    </Space>
                  ),
                },
                {
                  dot: <RobotOutlined style={{ color: '#52c41a' }} />,
                  children: (
                    <Space direction="vertical" size={0}>
                      <Text strong>AI处理</Text>
                      <Text type="secondary">智能解析文档内容并生成招标书</Text>
                    </Space>
                  ),
                },
                {
                  dot: <CheckCircleOutlined style={{ color: '#faad14' }} />,
                  children: (
                    <Space direction="vertical" size={0}>
                      <Text strong>获取结果</Text>
                      <Text type="secondary">下载生成的招标书文档</Text>
                    </Space>
                  ),
                },
              ]}
            />
          </Card>
        </Col>
      </Row>

      {/* 系统提示 */}
      {(systemInfo.documentService === 'offline' || systemInfo.tenderService === 'offline') && (
        <Row style={{ marginTop: 24 }}>
          <Col span={24}>
            <Alert
              message="服务状态提醒"
              description="部分服务当前不可用，请检查服务是否正常启动。如需帮助，请查看API文档或联系系统管理员。"
              type="warning"
              showIcon
              action={
                <Space>
                  <Button size="small" onClick={() => window.open('http://localhost:8000/docs', '_blank')}>
                    文档API
                  </Button>
                  <Button size="small" onClick={() => window.open('http://localhost:8001/docs', '_blank')}>
                    招标API
                  </Button>
                </Space>
              }
            />
          </Col>
        </Row>
      )}
    </div>
  );
};

export default HomePage;