/**
 * 任务管理页面组件
 * 提供任务列表查看、状态监控、结果下载等功能
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Typography,
  message,
  Modal,
  Tooltip,
  Input,
  Select,
  DatePicker,
  Row,
  Col,
  Statistic,
  Progress,
  Popconfirm,
} from 'antd';
import {
  ReloadOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  SearchOutlined,
  FilterOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  LoadingOutlined,
} from '@ant-design/icons';
import { tenderService } from '../../services/apiService';
import { STATUS_MAP } from '../../config/apiConfig';
import ResultDisplay from '../common/ResultDisplay';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const TaskManager = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    dateRange: null,
    keyword: '',
  });
  const [statistics, setStatistics] = useState({
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
    failed: 0,
  });

  // 获取任务列表
  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      const taskList = await tenderService.getAllTasks();
      setTasks(taskList);
      
      // 计算统计信息
      const stats = {
        total: taskList.length,
        pending: taskList.filter(t => t.status === STATUS_MAP.PENDING).length,
        processing: taskList.filter(t => t.status === STATUS_MAP.PROCESSING).length,
        completed: taskList.filter(t => t.status === STATUS_MAP.COMPLETED).length,
        failed: taskList.filter(t => t.status === STATUS_MAP.FAILED).length,
      };
      setStatistics(stats);
    } catch (error) {
      console.error('获取任务列表失败:', error);
      message.error('获取任务列表失败');
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始加载
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // 删除任务
  const handleDeleteTask = useCallback(async (taskId) => {
    try {
      await tenderService.deleteTask(taskId);
      message.success('任务删除成功');
      fetchTasks(); // 重新加载任务列表
    } catch (error) {
      console.error('删除任务失败:', error);
      message.error('删除任务失败');
    }
  }, [fetchTasks]);

  // 查看任务详情
  const handleViewTask = useCallback(async (task) => {
    try {
      // 如果任务已完成，获取最新状态
      if (task.status === STATUS_MAP.COMPLETED) {
        const latestStatus = await tenderService.getTaskStatus(task.task_id);
        setSelectedTask({ ...task, ...latestStatus });
      } else {
        setSelectedTask(task);
      }
      setPreviewVisible(true);
    } catch (error) {
      console.error('获取任务详情失败:', error);
      setSelectedTask(task);
      setPreviewVisible(true);
    }
  }, []);

  // 下载结果
  const handleDownload = useCallback((task) => {
    if (task.result && task.result.tender_document) {
      const content = task.result.tender_document;
      const filename = `招标书_${task.task_id}_${new Date().toISOString().slice(0, 10)}.md`;
      
      const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      message.success('下载成功');
    } else {
      message.warning('该任务暂无可下载的结果');
    }
  }, []);

  // 状态标签渲染
  const renderStatusTag = (status) => {
    const statusConfig = {
      [STATUS_MAP.PENDING]: { color: 'default', icon: <ClockCircleOutlined />, text: '等待中' },
      [STATUS_MAP.PROCESSING]: { color: 'processing', icon: <LoadingOutlined />, text: '处理中' },
      [STATUS_MAP.COMPLETED]: { color: 'success', icon: <CheckCircleOutlined />, text: '已完成' },
      [STATUS_MAP.FAILED]: { color: 'error', icon: <ExclamationCircleOutlined />, text: '失败' },
    };
    
    const config = statusConfig[status] || statusConfig[STATUS_MAP.PENDING];
    
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  // 过滤任务
  const filteredTasks = tasks.filter(task => {
    // 状态过滤
    if (filters.status && task.status !== filters.status) {
      return false;
    }
    
    // 关键词过滤
    if (filters.keyword) {
      const keyword = filters.keyword.toLowerCase();
      return (
        task.task_id.toLowerCase().includes(keyword) ||
        (task.filename && task.filename.toLowerCase().includes(keyword))
      );
    }
    
    // 日期范围过滤
    if (filters.dateRange && filters.dateRange.length === 2) {
      const taskDate = new Date(task.created_at);
      const [startDate, endDate] = filters.dateRange;
      return taskDate >= startDate && taskDate <= endDate;
    }
    
    return true;
  });

  // 表格列定义
  const columns = [
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      width: 200,
      render: (text) => (
        <Text code style={{ fontSize: '12px' }}>
          {text.substring(0, 8)}...
        </Text>
      ),
    },
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      ellipsis: true,
      render: (text) => text || '未知文件',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: renderStatusTag,
      filters: [
        { text: '等待中', value: STATUS_MAP.PENDING },
        { text: '处理中', value: STATUS_MAP.PROCESSING },
        { text: '已完成', value: STATUS_MAP.COMPLETED },
        { text: '失败', value: STATUS_MAP.FAILED },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 120,
      render: (progress, record) => {
        if (record.status === STATUS_MAP.COMPLETED) {
          return <Progress percent={100} size="small" status="success" />;
        } else if (record.status === STATUS_MAP.FAILED) {
          return <Progress percent={0} size="small" status="exception" />;
        } else if (record.status === STATUS_MAP.PROCESSING) {
          return <Progress percent={progress || 0} size="small" status="active" />;
        }
        return <Progress percent={0} size="small" />;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => new Date(text).toLocaleString('zh-CN'),
      sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handleViewTask(record)}
            />
          </Tooltip>
          {record.status === STATUS_MAP.COMPLETED && (
            <Tooltip title="下载结果">
              <Button
                type="text"
                icon={<DownloadOutlined />}
                onClick={() => handleDownload(record)}
              />
            </Tooltip>
          )}
          <Popconfirm
            title="确定要删除这个任务吗？"
            onConfirm={() => handleDeleteTask(record.task_id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除任务">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="task-manager">
      <Title level={2}>任务管理</Title>
      <Text type="secondary">
        查看和管理所有招标书生成任务，监控任务状态和下载结果
      </Text>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginTop: 24, marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总任务数" value={statistics.total} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="等待中" 
              value={statistics.pending} 
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="处理中" 
              value={statistics.processing} 
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已完成" 
              value={statistics.completed} 
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 过滤器 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Space>
              <Input
                placeholder="搜索任务ID或文件名"
                prefix={<SearchOutlined />}
                value={filters.keyword}
                onChange={(e) => setFilters(prev => ({ ...prev, keyword: e.target.value }))}
                style={{ width: 200 }}
              />
              <Select
                placeholder="状态筛选"
                value={filters.status}
                onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
                style={{ width: 120 }}
                allowClear
              >
                <Option value={STATUS_MAP.PENDING}>等待中</Option>
                <Option value={STATUS_MAP.PROCESSING}>处理中</Option>
                <Option value={STATUS_MAP.COMPLETED}>已完成</Option>
                <Option value={STATUS_MAP.FAILED}>失败</Option>
              </Select>
              <RangePicker
                placeholder={['开始日期', '结束日期']}
                value={filters.dateRange}
                onChange={(dates) => setFilters(prev => ({ ...prev, dateRange: dates }))}
              />
            </Space>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={fetchTasks}
              loading={loading}
            >
              刷新
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 任务列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredTasks}
          rowKey="task_id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* 任务详情模态框 */}
      <Modal
        title="任务详情"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={1000}
      >
        {selectedTask && (
          <ResultDisplay
            result={selectedTask}
            type="tender"
            title={`任务 ${selectedTask.task_id.substring(0, 8)}... 详情`}
            showMetadata={true}
            showActions={true}
          />
        )}
      </Modal>
    </div>
  );
};

export default TaskManager;