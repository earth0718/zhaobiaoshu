/**
 * 加载状态组件
 * 提供统一的加载状态显示
 */

import React from 'react';
import { Spin, Card, Typography, Progress, Space } from 'antd';
import { LoadingOutlined, FileTextOutlined, RobotOutlined } from '@ant-design/icons';

const { Text, Title } = Typography;

// 自定义加载图标
const customLoadingIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;

const LoadingSpinner = ({
  loading = true,
  size = 'default',
  tip = '加载中...',
  description = null,
  progress = null,
  type = 'default', // default, document, tender
  children = null,
}) => {
  // 根据类型选择图标和文案
  const getLoadingConfig = () => {
    switch (type) {
      case 'document':
        return {
          icon: <FileTextOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
          tip: '正在解析文档...',
          description: '请稍候，正在处理您的文档',
        };
      case 'tender':
        return {
          icon: <RobotOutlined style={{ fontSize: 24, color: '#52c41a' }} />,
          tip: '正在生成招标书...',
          description: 'AI正在为您生成专业的招标书文档',
        };
      default:
        return {
          icon: customLoadingIcon,
          tip,
          description,
        };
    }
  };

  const config = getLoadingConfig();

  // 简单加载状态
  if (!description && !progress && !children) {
    return (
      <Spin
        spinning={loading}
        size={size}
        tip={config.tip}
        indicator={config.icon}
      >
        {children}
      </Spin>
    );
  }

  // 详细加载状态
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        minHeight: '200px',
        padding: '20px'
      }}>
        <Card
          style={{ 
            textAlign: 'center',
            minWidth: '300px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
          }}
        >
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div>
              {config.icon}
            </div>
            
            <div>
              <Title level={4} style={{ margin: 0 }}>
                {config.tip}
              </Title>
              {config.description && (
                <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
                  {config.description}
                </Text>
              )}
            </div>

            {progress !== null && (
              <div style={{ width: '100%' }}>
                <Progress
                  percent={progress}
                  status={progress === 100 ? 'success' : 'active'}
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': '#87d068',
                  }}
                />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {progress}% 完成
                </Text>
              </div>
            )}

            {type === 'tender' && (
              <div style={{ marginTop: 16 }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  💡 提示：生成过程可能需要几分钟时间，请耐心等待
                </Text>
              </div>
            )}
          </Space>
        </Card>
      </div>
    );
  }

  return children;
};

// 页面级加载组件
export const PageLoading = ({ tip = '页面加载中...', description }) => (
  <div style={{
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    zIndex: 9999,
  }}>
    <LoadingSpinner
      loading={true}
      tip={tip}
      description={description}
      size="large"
    />
  </div>
);

// 内容区域加载组件
export const ContentLoading = ({ tip, description, height = '400px' }) => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height,
    backgroundColor: '#fafafa',
    borderRadius: '6px',
  }}>
    <LoadingSpinner
      loading={true}
      tip={tip}
      description={description}
    />
  </div>
);

// 按钮加载状态
export const ButtonLoading = ({ loading, children, ...props }) => (
  <Spin spinning={loading} indicator={<LoadingOutlined />}>
    {children}
  </Spin>
);

export default LoadingSpinner;