/**
 * 关于页面组件
 * 展示系统信息、技术栈、版本信息等
 */

import React from 'react';
import {
  Row,
  Col,
  Card,
  Typography,
  Space,
  Tag,
  Descriptions,
  Timeline,
  Alert,
  Button,
  Divider,
} from 'antd';
import {
  GithubOutlined,
  ApiOutlined,
  BugOutlined,
  QuestionCircleOutlined,
  RocketOutlined,
  TeamOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  GlobalOutlined,
  CloudOutlined,
} from '@ant-design/icons';

const { Title, Paragraph, Text, Link } = Typography;

const AboutPage = () => {
  // 技术栈信息
  const techStack = {
    frontend: [
      { name: 'React', version: '18.x', description: '用户界面库' },
      { name: 'Ant Design', version: '5.x', description: 'UI组件库' },
      { name: 'React Router', version: '6.x', description: '路由管理' },
      { name: 'Axios', version: '1.x', description: 'HTTP客户端' },
    ],
    backend: [
      { name: 'FastAPI', version: '0.104+', description: 'Web框架' },
      { name: 'Python', version: '3.8+', description: '编程语言' },
      { name: 'Uvicorn', version: '0.24+', description: 'ASGI服务器' },
      { name: 'PyMuPDF', version: '1.23+', description: 'PDF处理' },
      { name: 'python-docx', version: '1.1+', description: 'Word文档处理' },
    ],
    ai: [
      { name: 'Ollama', version: 'Latest', description: '本地大语言模型' },
      { name: 'DeepSeek API', version: 'v1', description: '云端AI服务' },
      { name: 'LangChain', version: '0.1+', description: '文本分割工具' },
    ],
  };

  // 系统特性
  const features = [
    {
      icon: <ThunderboltOutlined style={{ color: '#faad14' }} />,
      title: '高性能处理',
      description: '采用异步处理架构，支持大文件和批量处理，提供实时进度反馈。',
    },
    {
      icon: <SafetyCertificateOutlined style={{ color: '#52c41a' }} />,
      title: '安全可靠',
      description: '文件加密传输，处理完成后自动清理临时文件，保护用户数据安全。',
    },
    {
      icon: <GlobalOutlined style={{ color: '#1890ff' }} />,
      title: '多模型支持',
      description: '支持多种AI模型，可根据需求选择最适合的模型进行文档处理。',
    },
    {
      icon: <ApiOutlined style={{ color: '#722ed1' }} />,
      title: 'RESTful API',
      description: '提供完整的API接口，支持第三方系统集成和自定义开发。',
    },
    {
      icon: <CloudOutlined style={{ color: '#13c2c2' }} />,
      title: '云端部署',
      description: '支持容器化部署，可快速部署到云端或本地服务器。',
    },
    {
      icon: <TeamOutlined style={{ color: '#eb2f96' }} />,
      title: '团队协作',
      description: '支持多用户使用，任务管理和历史记录，便于团队协作。',
    },
  ];

  // 版本历史
  const versionHistory = [
    {
      version: 'v1.0.0',
      date: '2024-01-15',
      changes: [
        '初始版本发布',
        '支持PDF、Word、TXT、MD文档解析',
        '基础招标书生成功能',
        'Web界面和API接口',
      ],
    },
    {
      version: 'v1.1.0',
      date: '2024-02-01',
      changes: [
        '增加批量处理功能',
        '优化AI模型性能',
        '改进用户界面体验',
        '增加任务管理功能',
      ],
    },
    {
      version: 'v1.2.0',
      date: '2024-02-15',
      changes: [
        '支持更多文档格式',
        '增加质量控制选项',
        '优化错误处理机制',
        '增加系统监控功能',
      ],
    },
  ];

  // 渲染技术栈卡片
  const renderTechCard = (title, techs, color) => (
    <Card title={title} size="small">
      <Space direction="vertical" style={{ width: '100%' }}>
        {techs.map((tech, index) => (
          <Row key={index} justify="space-between" align="middle">
            <Col>
              <Space>
                <Text strong>{tech.name}</Text>
                <Tag color={color}>{tech.version}</Tag>
              </Space>
            </Col>
            <Col>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {tech.description}
              </Text>
            </Col>
          </Row>
        ))}
      </Space>
    </Card>
  );

  return (
    <div>
      {/* 系统介绍 */}
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div style={{ textAlign: 'center' }}>
                <RocketOutlined style={{ fontSize: '64px', color: '#1890ff' }} />
                <Title level={1} style={{ marginTop: 16 }}>
                  招标书文档解析系统
                </Title>
                <Paragraph style={{ fontSize: '18px', maxWidth: '800px', margin: '0 auto' }}>
                  基于人工智能技术的智能文档处理平台，专注于招标文档的解析和生成。
                  系统采用先进的自然语言处理技术，能够自动理解文档内容，
                  提取关键信息，并生成符合标准的招标书文档。
                </Paragraph>
              </div>
              
              <Alert
                message="开源项目"
                description="本项目采用开源协议，欢迎开发者参与贡献和改进。"
                type="info"
                showIcon
                action={
                  <Button
                    size="small"
                    icon={<GithubOutlined />}
                    onClick={() => window.open('https://github.com', '_blank')}
                  >
                    查看源码
                  </Button>
                }
              />
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 系统特性 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Title level={3}>系统特性</Title>
        </Col>
        {features.map((feature, index) => (
          <Col key={index} xs={24} md={12} lg={8}>
            <Card size="small" style={{ height: '100%' }}>
              <Space direction="vertical" size="small">
                <Space>
                  {feature.icon}
                  <Text strong>{feature.title}</Text>
                </Space>
                <Paragraph style={{ margin: 0 }}>
                  {feature.description}
                </Paragraph>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 技术栈 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Title level={3}>技术栈</Title>
        </Col>
        <Col xs={24} lg={8}>
          {renderTechCard('前端技术', techStack.frontend, 'blue')}
        </Col>
        <Col xs={24} lg={8}>
          {renderTechCard('后端技术', techStack.backend, 'green')}
        </Col>
        <Col xs={24} lg={8}>
          {renderTechCard('AI技术', techStack.ai, 'purple')}
        </Col>
      </Row>

      {/* 系统信息 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="系统信息">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="系统名称">
                招标书文档解析系统
              </Descriptions.Item>
              <Descriptions.Item label="当前版本">
                <Tag color="blue">v1.2.0</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="发布日期">
                2024年2月15日
              </Descriptions.Item>
              <Descriptions.Item label="开发语言">
                Python + JavaScript
              </Descriptions.Item>
              <Descriptions.Item label="部署方式">
                Docker + Nginx
              </Descriptions.Item>
              <Descriptions.Item label="数据库">
                SQLite / PostgreSQL
              </Descriptions.Item>
              <Descriptions.Item label="许可证">
                MIT License
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="版本历史">
            <Timeline
              size="small"
              items={versionHistory.map(version => ({
                children: (
                  <Space direction="vertical" size={0}>
                    <Space>
                      <Text strong>{version.version}</Text>
                      <Text type="secondary">{version.date}</Text>
                    </Space>
                    <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                      {version.changes.map((change, index) => (
                        <li key={index}>
                          <Text style={{ fontSize: '12px' }}>{change}</Text>
                        </li>
                      ))}
                    </ul>
                  </Space>
                ),
              }))}
            />
          </Card>
        </Col>
      </Row>

      {/* API文档和帮助 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="API文档和帮助">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={6}>
                <Button
                  block
                  icon={<ApiOutlined />}
                  onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                >
                  文档解析API
                </Button>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Button
                  block
                  icon={<ApiOutlined />}
                  onClick={() => window.open('http://localhost:8001/docs', '_blank')}
                >
                  招标生成API
                </Button>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Button
                  block
                  icon={<QuestionCircleOutlined />}
                  onClick={() => window.open('https://github.com', '_blank')}
                >
                  使用帮助
                </Button>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Button
                  block
                  icon={<BugOutlined />}
                  onClick={() => window.open('https://github.com', '_blank')}
                >
                  问题反馈
                </Button>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 联系信息 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="联系我们">
            <Row gutter={[24, 24]}>
              <Col xs={24} md={12}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Title level={5}>技术支持</Title>
                  <Paragraph>
                    如果您在使用过程中遇到任何问题，或者有功能建议，
                    欢迎通过以下方式联系我们：
                  </Paragraph>
                  <Space direction="vertical">
                    <Text>📧 邮箱: support@example.com</Text>
                    <Text>🐛 问题反馈: 
                      <Link href="https://github.com" target="_blank">
                        GitHub Issues
                      </Link>
                    </Text>
                    <Text>📖 文档: 
                      <Link href="https://docs.example.com" target="_blank">
                        在线文档
                      </Link>
                    </Text>
                  </Space>
                </Space>
              </Col>
              
              <Col xs={24} md={12}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Title level={5}>开发团队</Title>
                  <Paragraph>
                    本系统由专业的AI和文档处理团队开发，
                    致力于为用户提供高质量的智能文档处理服务。
                  </Paragraph>
                  <Space direction="vertical">
                    <Text>🏢 组织: AI文档处理实验室</Text>
                    <Text>👥 团队: 全栈开发 + AI算法</Text>
                    <Text>🌐 官网: 
                      <Link href="https://example.com" target="_blank">
                        www.example.com
                      </Link>
                    </Text>
                  </Space>
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 免责声明 */}
      <Row style={{ marginTop: 24 }}>
        <Col span={24}>
          <Alert
            message="免责声明"
            description={
              <div>
                <Paragraph style={{ margin: 0 }}>
                  本系统仅供学习和研究使用。生成的招标书文档仅作为参考，
                  用户应根据实际需求进行调整和完善。系统不对生成内容的准确性、
                  完整性或适用性承担责任。
                </Paragraph>
                <Divider style={{ margin: '12px 0' }} />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  使用本系统即表示您同意遵守相关法律法规，并承担使用风险。
                  如有疑问，请咨询专业法律人士。
                </Text>
              </div>
            }
            type="warning"
            showIcon
          />
        </Col>
      </Row>
    </div>
  );
};

export default AboutPage;