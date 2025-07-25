/**
 * 文件上传组件
 * 支持拖拽上传、文件验证、进度显示等功能
 */

import React, { useState, useCallback } from 'react';
import {
  Upload,
  Button,
  message,
  Progress,
  Card,
  Typography,
  Space,
  Tag,
  Tooltip,
} from 'antd';
import {
  InboxOutlined,
  UploadOutlined,
  FileTextOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { apiUtils } from '../../services/apiService';
import { API_CONFIG } from '../../config/apiConfig';

const { Dragger } = Upload;
const { Text, Paragraph } = Typography;

const FileUpload = ({
  onFileSelect,
  onFileRemove,
  multiple = false,
  accept = '.pdf,.docx,.doc,.txt,.md',
  maxCount = 1,
  disabled = false,
  showFileList = true,
  uploadText = '点击或拖拽文件到此区域上传',
  uploadHint = '支持PDF、Word、TXT、Markdown等格式',
}) => {
  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);

  // 文件验证
  const validateFile = useCallback((file) => {
    // 检查文件大小
    if (!apiUtils.validateFileSize(file)) {
      message.error(`文件 "${file.name}" 大小超过限制（${API_CONFIG.UPLOAD.MAX_FILE_SIZE / 1024 / 1024}MB）`);
      return false;
    }

    // 检查文件类型
    if (!apiUtils.validateFileType(file)) {
      message.error(`文件 "${file.name}" 格式不支持`);
      return false;
    }

    return true;
  }, []);

  // 处理文件选择
  const handleFileChange = useCallback((info) => {
    let newFileList = [...info.fileList];

    // 限制文件数量
    if (maxCount && newFileList.length > maxCount) {
      newFileList = newFileList.slice(-maxCount);
      message.warning(`最多只能上传 ${maxCount} 个文件`);
    }

    // 更新文件状态
    newFileList = newFileList.map((file) => {
      if (file.response) {
        file.url = file.response.url;
      }
      return file;
    });

    setFileList(newFileList);

    // 通知父组件
    if (info.file.status === 'done') {
      message.success(`文件 "${info.file.name}" 上传成功`);
      onFileSelect?.(info.file.originFileObj, newFileList);
    } else if (info.file.status === 'error') {
      message.error(`文件 "${info.file.name}" 上传失败`);
    }
  }, [maxCount, onFileSelect]);

  // 自定义上传逻辑
  const customRequest = useCallback(({ file, onSuccess, onError, onProgress }) => {
    // 验证文件
    if (!validateFile(file)) {
      onError(new Error('文件验证失败'));
      return;
    }

    setUploading(true);

    // 模拟上传进度
    let progress = 0;
    const timer = setInterval(() => {
      progress += Math.random() * 30;
      if (progress > 90) {
        progress = 90;
      }
      onProgress({ percent: Math.round(progress) });
    }, 200);

    // 模拟上传完成
    setTimeout(() => {
      clearInterval(timer);
      onProgress({ percent: 100 });
      onSuccess({
        name: file.name,
        size: file.size,
        type: file.type,
        url: URL.createObjectURL(file),
      });
      setUploading(false);
    }, 1000 + Math.random() * 2000);
  }, [validateFile]);

  // 移除文件
  const handleRemove = useCallback((file) => {
    const newFileList = fileList.filter(item => item.uid !== file.uid);
    setFileList(newFileList);
    onFileRemove?.(file, newFileList);
    message.info(`已移除文件 "${file.name}"`);
  }, [fileList, onFileRemove]);

  // 预览文件
  const handlePreview = useCallback((file) => {
    if (file.url || file.preview) {
      window.open(file.url || file.preview, '_blank');
    }
  }, []);

  // 渲染文件信息
  const renderFileInfo = (file) => {
    const fileSize = apiUtils.formatFileSize(file.size || 0);
    const fileType = apiUtils.getFileTypeDescription(file.originFileObj || file);
    
    return (
      <Card
        size="small"
        style={{ marginTop: 8 }}
        actions={[
          <Tooltip title="预览">
            <EyeOutlined onClick={() => handlePreview(file)} />
          </Tooltip>,
          <Tooltip title="移除">
            <DeleteOutlined onClick={() => handleRemove(file)} />
          </Tooltip>,
        ]}
      >
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Space>
            <FileTextOutlined />
            <Text strong>{file.name}</Text>
          </Space>
          <Space>
            <Tag color="blue">{fileType}</Tag>
            <Tag color="green">{fileSize}</Tag>
          </Space>
          {file.status === 'uploading' && (
            <Progress
              percent={file.percent}
              size="small"
              status="active"
            />
          )}
          {file.status === 'error' && (
            <Text type="danger">上传失败</Text>
          )}
        </Space>
      </Card>
    );
  };

  const uploadProps = {
    name: 'file',
    multiple,
    accept,
    fileList,
    customRequest,
    onChange: handleFileChange,
    onRemove: handleRemove,
    onPreview: handlePreview,
    disabled: disabled || uploading,
    showUploadList: false, // 使用自定义文件列表
  };

  return (
    <div className="file-upload-container">
      <Dragger {...uploadProps}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">{uploadText}</p>
        <p className="ant-upload-hint">
          {uploadHint}
          <br />
          <Text type="secondary">
            单个文件最大 {API_CONFIG.UPLOAD.MAX_FILE_SIZE / 1024 / 1024}MB
            {maxCount > 1 && `，最多 ${maxCount} 个文件`}
          </Text>
        </p>
      </Dragger>

      {/* 自定义文件列表 */}
      {showFileList && fileList.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <Typography.Title level={5}>已选择的文件：</Typography.Title>
          {fileList.map((file) => (
            <div key={file.uid}>
              {renderFileInfo(file)}
            </div>
          ))}
        </div>
      )}

      {/* 上传按钮（备用） */}
      {!fileList.length && (
        <div style={{ marginTop: 16, textAlign: 'center' }}>
          <Upload {...uploadProps}>
            <Button
              icon={<UploadOutlined />}
              disabled={disabled || uploading}
              loading={uploading}
            >
              选择文件
            </Button>
          </Upload>
        </div>
      )}
    </div>
  );
};

export default FileUpload;