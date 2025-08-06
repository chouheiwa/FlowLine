import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Button, Space, Form, Input, Table, Tag, message, Modal } from 'antd'
import { ReloadOutlined, ClearOutlined, PlusOutlined } from '@ant-design/icons'
import { useAppStore } from '../store'
import { taskApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'
import type { TaskInfo } from '../types'

const { TextArea } = Input

const TasksPage: React.FC = () => {
  const { tasks, loading, fetchTasks } = useAppStore()
  const [form] = Form.useForm()
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [selectedTask, setSelectedTask] = useState<TaskInfo | null>(null)

  useEffect(() => {
    fetchTasks()
    
    const interval = setInterval(() => {
      fetchTasks()
    }, 10000)
    
    return () => clearInterval(interval)
  }, [fetchTasks])

  const handleRefresh = () => {
    fetchTasks()
    message.success('数据刷新成功')
  }

  const handleClearCompleted = () => {
    message.success('已清空完成/失败的任务')
  }

  const handleCreateTask = async (values: { name: string; command: string }) => {
    try {
      await taskApi.createTask(values)
      message.success('任务创建成功')
      setCreateModalVisible(false)
      form.resetFields()
      fetchTasks()
    } catch (error) {
      message.error('任务创建失败')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running': return 'success'
      case 'pending': return 'warning'
      case 'completed': return 'blue'
      case 'failed': return 'error'
      case 'killed': return 'default'
      default: return 'default'
    }
  }

  const getStatusCount = (status: string) => {
    if (status === 'all') return tasks.length
    return tasks.filter(task => task.status.toLowerCase() === status).length
  }

  const filteredTasks = selectedStatus === 'all' 
    ? tasks 
    : tasks.filter(task => task.status.toLowerCase() === selectedStatus)

  const taskColumns: ColumnsType<TaskInfo> = [
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      width: 100
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'PID',
      dataIndex: 'pid',
      key: 'pid',
      width: 80
    },
    {
      title: 'GPU',
      dataIndex: 'gpu_id',
      key: 'gpu_id',
      width: 60
    },
    {
      title: '用户',
      dataIndex: 'user',
      key: 'user',
      width: 80
    },
    {
      title: '开始时间',
      dataIndex: 'startTime',
      key: 'startTime',
      width: 150
    },
    {
      title: '运行时间',
      dataIndex: 'runTime',
      key: 'runTime',
      width: 100
    },
    {
      title: '命令',
      dataIndex: 'command',
      key: 'command',
      ellipsis: true,
      render: (command: string, record: TaskInfo) => (
        <span 
          style={{ cursor: 'pointer', color: '#1890ff' }}
          onClick={() => setSelectedTask(record)}
        >
          {command}
        </span>
      )
    }
  ]

  const statusCategories = [
    { key: 'all', label: '全部任务', color: '#1890ff' },
    { key: 'running', label: '运行', color: '#52c41a' },
    { key: 'pending', label: '等待', color: '#faad14' },
    { key: 'completed', label: '完成', color: '#1890ff' },
    { key: 'failed', label: '失败', color: '#ff4d4f' },
    { key: 'killed', label: '终止', color: '#8c8c8c' }
  ]

  return (
    <div className="page-container">
      <Row gutter={[16, 16]}>
        {/* 侧边栏 */}
        <Col span={6}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 任务分类 */}
            <Card 
              title="任务分类"
              extra={
                <Button 
                  icon={<ReloadOutlined />}
                  onClick={handleRefresh}
                  loading={loading}
                  size="small"
                >
                  刷新
                </Button>
              }
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                {statusCategories.map(category => (
                  <Card
                    key={category.key}
                    size="small"
                    hoverable
                    style={{
                      cursor: 'pointer',
                      border: selectedStatus === category.key ? `2px solid ${category.color}` : '1px solid #d9d9d9'
                    }}
                    onClick={() => setSelectedStatus(category.key)}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>{category.label}</span>
                      <Tag color={category.color}>{getStatusCount(category.key)}</Tag>
                    </div>
                  </Card>
                ))}
              </Space>
            </Card>

            {/* 创建任务 */}
            <Card title="创建任务">
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
                block
              >
                创建新任务
              </Button>
            </Card>
          </Space>
        </Col>

        {/* 主内容区 */}
        <Col span={18}>
          <Card 
            title={`${statusCategories.find(c => c.key === selectedStatus)?.label || '任务列表'} (${filteredTasks.length})`}
            extra={
              <Button 
                icon={<ClearOutlined />}
                onClick={handleClearCompleted}
              >
                清空完成/失败
              </Button>
            }
          >
            <Table
              dataSource={filteredTasks}
              columns={taskColumns}
              rowKey="process_id"
              size="small"
              scroll={{ x: 1000 }}
              pagination={{
                pageSize: 15,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 创建任务模态框 */}
      <Modal
        title="创建新任务"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateTask}
        >
          <Form.Item
            name="name"
            label="任务名称"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="输入任务名称" />
          </Form.Item>
          
          <Form.Item
            name="command"
            label="命令"
            rules={[{ required: true, message: '请输入任务命令' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="输入任务命令"
            />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                创建任务
              </Button>
              <Button onClick={() => setCreateModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 任务详情模态框 */}
      <Modal
        title="任务详情"
        open={!!selectedTask}
        onCancel={() => setSelectedTask(null)}
        footer={[
          <Button key="close" onClick={() => setSelectedTask(null)}>
            关闭
          </Button>
        ]}
      >
        {selectedTask && (
          <div>
            <p><strong>任务ID:</strong> {selectedTask.task_id}</p>
            <p><strong>进程ID:</strong> {selectedTask.process_id}</p>
            <p><strong>PID:</strong> {selectedTask.pid}</p>
            <p><strong>状态:</strong> <Tag color={getStatusColor(selectedTask.status)}>{selectedTask.status.toUpperCase()}</Tag></p>
            <p><strong>GPU:</strong> {selectedTask.gpu_id}</p>
            <p><strong>用户:</strong> {selectedTask.user}</p>
            <p><strong>开始时间:</strong> {selectedTask.startTime}</p>
            <p><strong>运行时间:</strong> {selectedTask.runTime}</p>
            <p><strong>命令:</strong></p>
            <pre style={{ background: '#f5f5f5', padding: '8px', borderRadius: '4px' }}>
              {selectedTask.command}
            </pre>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default TasksPage