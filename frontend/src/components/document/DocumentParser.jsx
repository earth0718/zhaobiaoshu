/**
 * 文档解析页面组件
 * 提供文档上传、解析选项配置和结果展示功能
 */

import React, { useState, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Form,
  Switch,
  InputNumber,
  Button,
  Space,
  Alert,
  Divider,
  Typography,
  Radio,
  Input,
  message,
} from 'antd';
import {
  FileTextOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  ClearOutlined,
} from '@ant-design/icons';
import FileUpload from '../common/FileUpload';
import LoadingSpinner from '../common/LoadingSpinner';
import ResultDisplay from '../common/ResultDisplay';
import { documentService } from '../../services/apiService';

const { Title, Text } = Typography;
const { TextArea } = Input;

const DocumentParser = () => {
  const [form] = Form.useForm();
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [parseType, setParseType] = useState('parse'); // parse, extract-text, extract-structured

  // 处理文件选择
  const handleFileSelect = useCallback((file) => {
    setSelectedFile(file);
    setResult(null); // 清除之前的结果
    message.info(`已选择文件: ${file.name}`);
  }, []);

  // 处理文件移除
  const handleFileRemove = useCallback(() => {
    setSelectedFile(null);
    setResult(null);
    message.info('已移除文件');
  }, []);

  // 执行文档解析
  const handleParse = useCallback(async () => {
    if (!selectedFile) {
      message.warning('请先选择要解析的文件');
      return;
    }

    try {
      setLoading(true);
      setResult(null);

      const formValues = form.getFieldsValue();
      let parseResult;

      switch (parseType) {
        case 'parse':
          parseResult = await documentService.parseDocument(selectedFile, {
            include_metadata: formValues.include_metadata,
            cleanup: formValues.cleanup,
            max_pages_per_batch: formValues.max_pages_per_batch,
          });
          break;

        case 'extract-text':
          parseResult = await documentService.extractText(
            selectedFile,
            formValues.max_length || null
          );
          break;

        case 'extract-structured':
          parseResult = await documentService.extractStructured(
            selectedFile,
            formValues.target_types || null
          );
          break;

        default:
          throw new Error('未知的解析类型');
      }

      setResult(parseResult);
      message.success('文档解析完成');
    } catch (error) {
      console.error('解析失败:', error);
      message.error(`解析失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [selectedFile, parseType, form]);

  // 清除所有内容
  const handleClear = useCallback(() => {
    setSelectedFile(null);
    setResult(null);
    form.resetFields();
    message.info('已清除所有内容');
  }, [form]);

  // 渲染解析选项
  const renderParseOptions = () => {
    switch (parseType) {
      case 'parse':
        return (
          <>
            <Form.Item
              name="include_metadata"
              label="包含元数据"
              valuePropName="checked"
              initialValue={true}
            >
              <Switch />
            </Form.Item>
            <Form.Item
              name="cleanup"
              label="清理临时文件"
              valuePropName="checked"
              initialValue={true}
            >
              <Switch />
            </Form.Item>
            <Form.Item
              name="max_pages_per_batch"
              label="每批最大页数"
              initialValue={5}
              rules={[
                { type: 'number', min: 1, max: 20, message: '页数范围: 1-20' }
              ]}
            >
              <InputNumber min={1} max={20} style={{ width: '100%' }} />
            </Form.Item>
          </>
        );

      case 'extract-text':
        return (
          <Form.Item
            name="max_length"
            label="最大文本长度"
            help="留空表示不限制长度"
          >
            <InputNumber
              min={1}
              placeholder="如: 10000"
              style={{ width: '100%' }}
            />
          </Form.Item>
        );

      case 'extract-structured':
        return (
          <Form.Item
            name="target_types"
            label="目标元素类型"
            help="多个类型用逗号分隔，如: Title,Table,List"
          >
            <Input placeholder="Title,Table,List,NarrativeText" />
          </Form.Item>
        );

      default:
        return null;
    }
  };

  return (
    <div className="document-parser">
      <Title level={2}>
        <FileTextOutlined /> 文档解析
      </Title>
      <Text type="secondary">
        支持PDF、Word、TXT、Markdown等格式的文档解析，提取文本内容和结构化数据
      </Text>

      <Divider />

      <Row gutter={[24, 24]}>
        {/* 左侧：文件上传和配置 */}
        <Col xs={24} lg={12}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {/* 文件上传 */}
            <Card title="文件上传" size="small">
              <FileUpload
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
                accept=".pdf,.docx,.doc,.txt,.md"
                uploadText="选择要解析的文档"
                uploadHint="支持PDF、Word、TXT、Markdown格式"
              />
            </Card>

            {/* 解析类型选择 */}
            <Card title="解析类型" size="small">
              <Radio.Group
                value={parseType}
                onChange={(e) => setParseType(e.target.value)}
                style={{ width: '100%' }}
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Radio value="parse">
                    <strong>完整解析</strong>
                    <br />
                    <Text type="secondary">解析文档并返回完整的JSON结构</Text>
                  </Radio>
                  <Radio value="extract-text">
                    <strong>提取纯文本</strong>
                    <br />
                    <Text type="secondary">仅提取文档中的文本内容</Text>
                  </Radio>
                  <Radio value="extract-structured">
                    <strong>提取结构化数据</strong>
                    <br />
                    <Text type="secondary">提取标题、表格、列表等结构化元素</Text>
                  </Radio>
                </Space>
              </Radio.Group>
            </Card>

            {/* 解析选项 */}
            <Card
              title={
                <Space>
                  <SettingOutlined />
                  <span>解析选项</span>
                </Space>
              }
              size="small"
            >
              <Form form={form} layout="vertical">
                {renderParseOptions()}
              </Form>
            </Card>

            {/* 操作按钮 */}
            <Card size="small">
              <Space style={{ width: '100%', justifyContent: 'center' }}>
                <Button
                  type="primary"
                  size="large"
                  icon={<PlayCircleOutlined />}
                  onClick={handleParse}
                  disabled={!selectedFile || loading}
                  loading={loading}
                >
                  开始解析
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
          </Space>
        </Col>

        {/* 右侧：结果展示 */}
        <Col xs={24} lg={12}>
          <Card title="解析结果" size="small" style={{ minHeight: '600px' }}>
            {loading ? (
              <LoadingSpinner
                loading={true}
                type="document"
                tip="正在解析文档..."
                description="请稍候，正在处理您的文档"
              />
            ) : result ? (
              <ResultDisplay
                result={result}
                type="document"
                title="文档解析结果"
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
                  <FileTextOutlined style={{ fontSize: '48px' }} />
                  <Text type="secondary">选择文件并点击"开始解析"查看结果</Text>
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
            <li><strong>完整解析</strong>：解析文档并返回包含文本、元数据和结构信息的完整JSON</li>
            <li><strong>提取纯文本</strong>：仅提取文档中的纯文本内容，适合文本分析</li>
            <li><strong>提取结构化数据</strong>：提取标题、表格、列表等特定类型的结构化元素</li>
            <li>支持的文件格式：PDF、Word(.docx/.doc)、TXT、Markdown</li>
            <li>单个文件最大50MB，建议文档页数不超过100页以获得最佳性能</li>
          </ul>
        }
        type="info"
        showIcon
      />
    </div>
  );
};

export default DocumentParser;