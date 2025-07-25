/**
 * 结果展示组件
 * 用于显示文档解析和招标书生成的结果
 */

import React, { useState } from 'react';
import {
  Card,
  Typography,
  Button,
  Space,
  Tabs,
  Tag,
  Descriptions,
  message,
  Modal,
  Tooltip,
  Divider,
} from 'antd';
import {
  DownloadOutlined,
  CopyOutlined,
  EyeOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

const ResultDisplay = ({
  result,
  type = 'document', // document, tender
  title = '处理结果',
  showMetadata = true,
  showActions = true,
  onDownload,
  onCopy,
  onPreview,
}) => {
  const [previewVisible, setPreviewVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('content');

  if (!result) {
    return null;
  }

  // 复制内容到剪贴板
  const handleCopy = async (content) => {
    try {
      await navigator.clipboard.writeText(content);
      message.success('内容已复制到剪贴板');
      onCopy?.(content);
    } catch (error) {
      message.error('复制失败，请手动复制');
    }
  };

  // 下载内容
  const handleDownload = (content, filename) => {
    try {
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      message.success('下载成功');
      onDownload?.(content, filename);
    } catch (error) {
      message.error('下载失败');
    }
  };

  // 预览内容
  const handlePreview = () => {
    setPreviewVisible(true);
    onPreview?.(result);
  };

  // 格式化时间
  const formatTime = (timeString) => {
    if (!timeString) return '未知';
    return new Date(timeString).toLocaleString('zh-CN');
  };

  // 格式化文件大小
  const formatFileSize = (bytes) => {
    if (!bytes) return '未知';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  // 渲染文档解析结果
  const renderDocumentResult = () => {
    const { content, metadata, elements } = result;

    return (
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="解析内容" key="content">
          <Card>
            <Paragraph>
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                wordBreak: 'break-word',
                maxHeight: '500px',
                overflow: 'auto',
                backgroundColor: '#f5f5f5',
                padding: '16px',
                borderRadius: '6px'
              }}>
                {typeof content === 'string' ? content : JSON.stringify(content, null, 2)}
              </pre>
            </Paragraph>
          </Card>
        </TabPane>

        {elements && (
          <TabPane tab="结构化数据" key="elements">
            <Card>
              {elements.map((element, index) => (
                <Card key={index} size="small" style={{ marginBottom: 8 }}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Space>
                      <Tag color="blue">{element.type}</Tag>
                      {element.metadata?.page_number && (
                        <Tag color="green">第 {element.metadata.page_number} 页</Tag>
                      )}
                    </Space>
                    <Text>{element.text}</Text>
                  </Space>
                </Card>
              ))}
            </Card>
          </TabPane>
        )}

        {metadata && showMetadata && (
          <TabPane tab="元数据" key="metadata">
            <Card>
              <Descriptions column={2} size="small">
                {Object.entries(metadata).map(([key, value]) => (
                  <Descriptions.Item key={key} label={key}>
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </Descriptions.Item>
                ))}
              </Descriptions>
            </Card>
          </TabPane>
        )}
      </Tabs>
    );
  };

  // 渲染招标书生成结果
  const renderTenderResult = () => {
    const { 
      tender_document, 
      file_size, 
      generation_time,
      task_id,
      status,
      created_at,
      updated_at 
    } = result;

    return (
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="招标书内容" key="content">
          <Card>
            <div style={{ maxHeight: '600px', overflow: 'auto' }}>
              <ReactMarkdown>{tender_document}</ReactMarkdown>
            </div>
          </Card>
        </TabPane>

        {showMetadata && (
          <TabPane tab="生成信息" key="metadata">
            <Card>
              <Descriptions column={2}>
                <Descriptions.Item label="任务ID">
                  <Text code>{task_id}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag color={status === 'completed' ? 'success' : 'processing'}>
                    {status === 'completed' ? '已完成' : '处理中'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="文件大小">
                  {formatFileSize(file_size)}
                </Descriptions.Item>
                <Descriptions.Item label="生成时间">
                  {formatTime(generation_time)}
                </Descriptions.Item>
                <Descriptions.Item label="创建时间">
                  {formatTime(created_at)}
                </Descriptions.Item>
                <Descriptions.Item label="更新时间">
                  {formatTime(updated_at)}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </TabPane>
        )}
      </Tabs>
    );
  };

  // 获取主要内容
  const getMainContent = () => {
    if (type === 'tender') {
      return result.tender_document || '';
    }
    return result.content || JSON.stringify(result, null, 2);
  };

  // 获取下载文件名
  const getDownloadFilename = () => {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    if (type === 'tender') {
      return `招标书_${timestamp}.md`;
    }
    return `文档解析结果_${timestamp}.txt`;
  };

  const mainContent = getMainContent();
  const filename = getDownloadFilename();

  return (
    <div className="result-display">
      <Card
        title={
          <Space>
            {type === 'tender' ? <FileTextOutlined /> : <InfoCircleOutlined />}
            <span>{title}</span>
            {result.status && (
              <Tag color={result.status === 'completed' ? 'success' : 'processing'}>
                {result.status === 'completed' ? '已完成' : '处理中'}
              </Tag>
            )}
          </Space>
        }
        extra={
          showActions && (
            <Space>
              <Tooltip title="预览">
                <Button
                  icon={<EyeOutlined />}
                  onClick={handlePreview}
                />
              </Tooltip>
              <Tooltip title="复制">
                <Button
                  icon={<CopyOutlined />}
                  onClick={() => handleCopy(mainContent)}
                />
              </Tooltip>
              <Tooltip title="下载">
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={() => handleDownload(mainContent, filename)}
                >
                  下载
                </Button>
              </Tooltip>
            </Space>
          )
        }
      >
        {type === 'tender' ? renderTenderResult() : renderDocumentResult()}
      </Card>

      {/* 预览模态框 */}
      <Modal
        title="内容预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="copy" onClick={() => handleCopy(mainContent)}>
            复制
          </Button>,
          <Button key="download" type="primary" onClick={() => handleDownload(mainContent, filename)}>
            下载
          </Button>,
        ]}
        width={800}
      >
        <div style={{ maxHeight: '500px', overflow: 'auto' }}>
          {type === 'tender' ? (
            <ReactMarkdown>{mainContent}</ReactMarkdown>
          ) : (
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {mainContent}
            </pre>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default ResultDisplay;