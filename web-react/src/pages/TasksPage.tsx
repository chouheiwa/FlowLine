import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Button, Space, Form, Input, Table, Tag, message, Modal, InputNumber, Tooltip } from 'antd'
import { ReloadOutlined, ClearOutlined, PlusOutlined, CopyOutlined, FolderOutlined } from '@ant-design/icons'
import { useAppStore } from '../store'
import { taskApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'
import type { TaskInfo, CreateTaskRequest, CopyTaskRequest } from '../types'

const { TextArea } = Input

const TasksPage: React.FC = () => {
  const { tasks, loading, fetchTasks } = useAppStore()
  const [form] = Form.useForm()
  const [copyForm] = Form.useForm()
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [copyModalVisible, setCopyModalVisible] = useState(false)
  const [selectedTask, setSelectedTask] = useState<TaskInfo | null>(null)
  const [taskToCopy, setTaskToCopy] = useState<TaskInfo | null>(null)

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

  const handleCreateTask = async (values: { name: string; cmd: string; working_dir?: string; need_run_num?: number }) => {
    try {
      const taskData: CreateTaskRequest = {
        name: values.name,
        cmd: values.cmd,
        working_dir: values.working_dir,
        need_run_num: values.need_run_num || 1
      }
      await taskApi.createTask(taskData)
      message.success('任务创建成功')
      setCreateModalVisible(false)
      form.resetFields()
      fetchTasks()
    } catch (error) {
      message.error('任务创建失败')
    }
  }

  const handleCopyTask = async (values: { new_name: string; need_run_num: number }) => {
    if (!taskToCopy) return
    
    try {
      const copyData: CopyTaskRequest = {
        original_task_id: parseInt(taskToCopy.task_id),
        new_name: values.new_name,
        need_run_num: values.need_run_num
      }
      await taskApi.copyTask(copyData)
      message.success('任务复制成功')
      setCopyModalVisible(false)
      copyForm.resetFields()
      setTaskToCopy(null)
      fetchTasks()
    } catch (error) {
      message.error('任务复制失败')
    }
  }

  const showCopyModal = (task: TaskInfo) => {
    setTaskToCopy(task)
    copyForm.setFieldsValue({
      new_name: `${task.name || task.command} - 副本`,
      need_run_num: task.need_run_num || 1
    })
    setCopyModalVisible(true)
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
      width: 80
    },
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      render: (name: string, record: TaskInfo) => (
        <span 
          style={{ cursor: 'pointer', color: '#1890ff' }}
          onClick={() => setSelectedTask(record)}
        >
          {name || record.command?.substring(0, 30) + '...'}
        </span>
      )
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
      title: '进度',
      key: 'progress',
      width: 80,
      render: (_, record: TaskInfo) => (
        <span>
          {record.run_num || 0}/{record.need_run_num || 1}
        </span>
      )
    },
    {
      title: '工作目录',
      dataIndex: 'working_dir',
      key: 'working_dir',
      width: 150,
      ellipsis: true,
      render: (working_dir: string) => (
        working_dir ? (
          <Tooltip title={working_dir}>
            <span>
              <FolderOutlined style={{ marginRight: 4 }} />
              {working_dir}
            </span>
          </Tooltip>
        ) : (
          <span style={{ color: '#999' }}>-</span>
        )
      )
    },
    {
      title: 'GPU',
      dataIndex: 'gpu_id',
      key: 'gpu_id',
      width: 60
    },
    {
      title: '开始时间',
      dataIndex: 'startTime',
      key: 'startTime',
      width: 150
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_, record: TaskInfo) => (
        <Space>
          <Tooltip title="复制任务">
            <Button
              type="text"
              icon={<CopyOutlined />}
              size="small"
              onClick={() => showCopyModal(record)}
            />
          </Tooltip>
        </Space>
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
            name="cmd"
            label="命令"
            rules={[{ required: true, message: '请输入任务命令' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="输入任务命令"
            />
          </Form.Item>

          <Form.Item
            name="working_dir"
            label="工作目录"
            tooltip="任务执行时的工作目录，留空则使用默认目录"
          >
            <Input 
              placeholder="/path/to/working/directory"
              prefix={<FolderOutlined />}
            />
          </Form.Item>

          <Form.Item
            name="need_run_num"
            label="运行次数"
            initialValue={1}
            rules={[{ required: true, message: '请输入运行次数' }]}
          >
            <InputNumber 
              min={1} 
              max={100}
              placeholder="1"
              style={{ width: '100%' }}
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
            <p><strong>任务名称:</strong> {selectedTask.name || '未命名'}</p>
            <p><strong>进程ID:</strong> {selectedTask.process_id}</p>
            <p><strong>PID:</strong> {selectedTask.pid}</p>
            <p><strong>状态:</strong> <Tag color={getStatusColor(selectedTask.status)}>{selectedTask.status.toUpperCase()}</Tag></p>
            <p><strong>进度:</strong> {selectedTask.run_num || 0}/{selectedTask.need_run_num || 1}</p>
            <p><strong>GPU:</strong> {selectedTask.gpu_id}</p>
            <p><strong>用户:</strong> {selectedTask.user}</p>
            <p><strong>工作目录:</strong> {selectedTask.working_dir || '默认'}</p>
            <p><strong>开始时间:</strong> {selectedTask.startTime}</p>
            <p><strong>运行时间:</strong> {selectedTask.runTime}</p>
            <p><strong>命令:</strong></p>
            <pre style={{ background: '#f5f5f5', padding: '8px', borderRadius: '4px' }}>
              {selectedTask.command}
            </pre>
            {selectedTask.config_dict && Object.keys(selectedTask.config_dict).length > 0 && (
              <>
                <p><strong>配置信息:</strong></p>
                <pre style={{ background: '#f5f5f5', padding: '8px', borderRadius: '4px' }}>
                  {JSON.stringify(selectedTask.config_dict, null, 2)}
                </pre>
              </>
            )}
          </div>
        )}
      </Modal>

      {/* 复制任务模态框 */}
      <Modal
        title="复制任务"
        open={copyModalVisible}
        onCancel={() => {
          setCopyModalVisible(false)
          setTaskToCopy(null)
          copyForm.resetFields()
        }}
        footer={null}
      >
        {taskToCopy && (
          <>
            <div style={{ marginBottom: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
              <p style={{ margin: 0 }}><strong>原始任务:</strong> {taskToCopy.name || taskToCopy.command}</p>
              <p style={{ margin: 0 }}><strong>任务ID:</strong> {taskToCopy.task_id}</p>
              <p style={{ margin: 0 }}><strong>工作目录:</strong> {taskToCopy.working_dir || '默认'}</p>
            </div>
            
            <Form
              form={copyForm}
              layout="vertical"
              onFinish={handleCopyTask}
            >
              <Form.Item
                name="new_name"
                label="新任务名称"
                rules={[{ required: true, message: '请输入新任务名称' }]}
              >
                <Input placeholder="输入新任务名称" />
              </Form.Item>
              
              <Form.Item
                name="need_run_num"
                label="运行次数"
                rules={[{ required: true, message: '请输入运行次数' }]}
              >
                <InputNumber 
                  min={1} 
                  max={100}
                  style={{ width: '100%' }}
                />
              </Form.Item>
              
              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit">
                    复制任务
                  </Button>
                  <Button onClick={() => {
                    setCopyModalVisible(false)
                    setTaskToCopy(null)
                    copyForm.resetFields()
                  }}>
                    取消
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </>
        )}
      </Modal>
    </div>
  )
}

export default TasksPage