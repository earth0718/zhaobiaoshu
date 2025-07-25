/**
 * 主布局组件
 * 提供应用的整体布局结构，包括导航、侧边栏、内容区域等
 */

import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Space, Button, Drawer, message } from 'antd';
import {
  FileTextOutlined,
  RobotOutlined,
  UnorderedListOutlined,
  SettingOutlined,
  MenuOutlined,
  HomeOutlined,
  ApiOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { documentService, tenderService } from '../../services/apiService';

const { Header, Sider, Content, Footer } = Layout;
const { Title, Text } = Typography;

const MainLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileDrawerVisible, setMobileDrawerVisible] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [serviceStatus, setServiceStatus] = useState({
    document: 'unknown',
    tender: 'unknown',
  });

  // 检测移动端
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // 检查服务状态
  useEffect(() => {
    const checkServices = async () => {
      try {
        await documentService.checkHealth();
        setServiceStatus(prev => ({ ...prev, document: 'online' }));
      } catch (error) {
        setServiceStatus(prev => ({ ...prev, document: 'offline' }));
      }

      try {
        await tenderService.checkHealth();
        setServiceStatus(prev => ({ ...prev, tender: 'online' }));
      } catch (error) {
        setServiceStatus(prev => ({ ...prev, tender: 'offline' }));
      }
    };

    checkServices();
    // 每30秒检查一次服务状态
    const interval = setInterval(checkServices, 30000);
    return () => clearInterval(interval);
  }, []);

  // 菜单项配置
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/document',
      icon: <FileTextOutlined />,
      label: '文档解析',
    },
    {
      key: '/tender',
      icon: <RobotOutlined />,
      label: '招标书生成',
    },
    {
      key: '/tasks',
      icon: <UnorderedListOutlined />,
      label: '任务管理',
    },
    {
      type: 'divider',
    },
    {
      key: '/api-docs',
      icon: <ApiOutlined />,
      label: 'API文档',
      children: [
        {
          key: 'http://localhost:8000/docs',
          label: '文档解析API',
          icon: <FileTextOutlined />,
        },
        {
          key: 'http://localhost:8001/docs',
          label: '招标生成API',
          icon: <RobotOutlined />,
        },
      ],
    },
    {
      key: '/about',
      icon: <InfoCircleOutlined />,
      label: '关于系统',
    },
  ];

  // 处理菜单点击
  const handleMenuClick = ({ key }) => {
    if (key.startsWith('http')) {
      // 外部链接
      window.open(key, '_blank');
    } else {
      // 内部路由
      navigate(key);
      if (isMobile) {
        setMobileDrawerVisible(false);
      }
    }
  };

  // 获取当前选中的菜单项
  const getSelectedKeys = () => {
    return [location.pathname];
  };

  // 渲染服务状态指示器
  const renderServiceStatus = () => {
    const getStatusColor = (status) => {
      switch (status) {
        case 'online': return '#52c41a';
        case 'offline': return '#ff4d4f';
        default: return '#faad14';
      }
    };

    const getStatusText = (status) => {
      switch (status) {
        case 'online': return '在线';
        case 'offline': return '离线';
        default: return '检查中';
      }
    };

    return (
      <Space size="small" style={{ fontSize: '12px' }}>
        <span>
          文档服务:
          <span style={{ color: getStatusColor(serviceStatus.document), marginLeft: 4 }}>
            {getStatusText(serviceStatus.document)}
          </span>
        </span>
        <span>
          招标服务:
          <span style={{ color: getStatusColor(serviceStatus.tender), marginLeft: 4 }}>
            {getStatusText(serviceStatus.tender)}
          </span>
        </span>
      </Space>
    );
  };

  // 侧边栏内容
  const siderContent = (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={getSelectedKeys()}
      items={menuItems}
      onClick={handleMenuClick}
      style={{ height: '100%', borderRight: 0 }}
    />
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 桌面端侧边栏 */}
      {!isMobile && (
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          width={250}
          style={{
            overflow: 'auto',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
          }}
        >
          <div style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderBottom: '1px solid #303030',
          }}>
            {!collapsed ? (
              <Title level={4} style={{ color: 'white', margin: 0 }}>
                招标解析系统
              </Title>
            ) : (
              <RobotOutlined style={{ color: 'white', fontSize: '24px' }} />
            )}
          </div>
          {siderContent}
        </Sider>
      )}

      {/* 移动端抽屉 */}
      {isMobile && (
        <Drawer
          title="招标解析系统"
          placement="left"
          onClose={() => setMobileDrawerVisible(false)}
          open={mobileDrawerVisible}
          bodyStyle={{ padding: 0 }}
        >
          {siderContent}
        </Drawer>
      )}

      <Layout style={{ marginLeft: isMobile ? 0 : (collapsed ? 80 : 250) }}>
        {/* 头部 */}
        <Header style={{
          padding: '0 24px',
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #f0f0f0',
          position: 'sticky',
          top: 0,
          zIndex: 1000,
        }}>
          <Space>
            {isMobile ? (
              <Button
                type="text"
                icon={<MenuOutlined />}
                onClick={() => setMobileDrawerVisible(true)}
              />
            ) : (
              <Button
                type="text"
                icon={<MenuOutlined />}
                onClick={() => setCollapsed(!collapsed)}
              />
            )}
            <Title level={4} style={{ margin: 0 }}>
              招标书文档解析系统
            </Title>
          </Space>
          
          <Space>
            {renderServiceStatus()}
          </Space>
        </Header>

        {/* 内容区域 */}
        <Content style={{
          margin: '24px',
          padding: '24px',
          background: '#fff',
          borderRadius: '8px',
          minHeight: 'calc(100vh - 112px)',
        }}>
          {children}
        </Content>

        {/* 底部 */}
        <Footer style={{
          textAlign: 'center',
          background: '#f0f2f5',
          padding: '12px 24px',
        }}>
          <Space direction="vertical" size={0}>
            <Text type="secondary">
              招标书文档解析系统 ©2024 - 基于AI技术的智能文档处理平台
            </Text>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              支持PDF、Word等多种格式 | 智能解析 | 自动生成招标书
            </Text>
          </Space>
        </Footer>
      </Layout>
    </Layout>
  );
};

export default MainLayout;