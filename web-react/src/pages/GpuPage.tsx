import React, { useEffect } from 'react'
import { Row, Col, Card, Button, Space, Progress, Table, Tag, message } from 'antd'
import { PlayCircleOutlined, ReloadOutlined, ClearOutlined } from '@ant-design/icons'
import { useAppStore } from '../store'
import type { ColumnsType } from 'antd/es/table'
import type { TaskInfo } from '../types'

const GpuPage: React.FC = () => {
  const {
    gpus,
    selectedGpuId,
    gpuTasks,
    tasks,
    loading,
    fetchGpus,
    fetchTasks,
    selectGpu,
    toggleSystem
  } = useAppStore()

  useEffect(() => {
    fetchGpus()
    fetchTasks()
    
    // 设置定时刷新
    const interval = setInterval(() => {
      fetchGpus()
      fetchTasks()
    }, 10000)
    
    return () => clearInterval(interval)
  }, [fetchGpus, fetchTasks])

  const handleRefresh = () => {
    fetchGpus()
    fetchTasks()
    message.success('数据刷新成功')
  }

  const handleRun = async () => {
    await toggleSystem()
    message.success('运行状态已切换')
    fetchGpus()
    fetchTasks()
  }

  const handleClearCompleted = () => {
    // TODO: 实现清空完成/失败任务的逻辑
    message.success('已清空完成/失败的任务')
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

  const processColumns: ColumnsType<TaskInfo> = [
    {
      title: '进程',
      dataIndex: 'process_id',
      key: 'process_id',
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
      title: '任务',
      dataIndex: 'task_id',
      key: 'task_id',
      width: 100
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
      ellipsis: true
    }
  ]

  return (
    <div className="page-container">
      <Row gutter={[16, 16]}>
        {/* GPU列表 */}
        <Col span={8}>
          <Card 
            title="GPU 列表" 
            extra={
              <Space>
                <Button 
                  type="primary" 
                  icon={<PlayCircleOutlined />}
                  onClick={handleRun}
                >
                  运行
                </Button>
                <Button 
                  icon={<ReloadOutlined />}
                  onClick={handleRefresh}
                  loading={loading}
                >
                  刷新
                </Button>
              </Space>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              {gpus.map(gpu => (
                <Card
                  key={gpu.gpu_id}
                  size="small"
                  hoverable
                  style={{
                    cursor: 'pointer',
                    border: selectedGpuId === gpu.gpu_id ? '2px solid #1890ff' : '1px solid #d9d9d9'
                  }}
                  onClick={() => selectGpu(gpu.gpu_id)}
                >
                  <div>
                    <strong>GPU {gpu.gpu_id}</strong> - {gpu.name}
                  </div>
                  <div style={{ marginTop: 8 }}>
                    <div>内存: {gpu.memory.used}GB / {gpu.memory.total}GB</div>
                    <Progress 
                      percent={Math.round((parseFloat(gpu.memory.used) / parseFloat(gpu.memory.total)) * 100)}
                      size="small"
                      status={parseFloat(gpu.memory.used) / parseFloat(gpu.memory.total) > 0.8 ? 'exception' : 'normal'}
                    />
                  </div>
                  <div style={{ marginTop: 4 }}>
                    <span>利用率: {gpu.utilization}%</span>
                    <span style={{ marginLeft: 16 }}>温度: {gpu.temperature}°C</span>
                  </div>
                </Card>
              ))}
            </Space>
          </Card>
        </Col>

        {/* GPU详情和任务 */}
        <Col span={16}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* GPU详情 */}
            {selectedGpuId && (
              <Card title={`GPU ${selectedGpuId} 详情`}>
                {gpus.find(gpu => gpu.gpu_id === selectedGpuId) && (
                  <Row gutter={16}>
                    <Col span={12}>
                      <p><strong>名称:</strong> {gpus.find(gpu => gpu.gpu_id === selectedGpuId)?.name}</p>
                      <p><strong>状态:</strong> {gpus.find(gpu => gpu.gpu_id === selectedGpuId)?.status}</p>
                      <p><strong>温度:</strong> {gpus.find(gpu => gpu.gpu_id === selectedGpuId)?.temperature}°C</p>
                    </Col>
                    <Col span={12}>
                      <p><strong>利用率:</strong> {gpus.find(gpu => gpu.gpu_id === selectedGpuId)?.utilization}%</p>
                      <p><strong>功耗:</strong> {gpus.find(gpu => gpu.gpu_id === selectedGpuId)?.power.current}W / {gpus.find(gpu => gpu.gpu_id === selectedGpuId)?.power.max}W</p>
                    </Col>
                  </Row>
                )}
              </Card>
            )}

            {/* 活跃任务 */}
            {selectedGpuId && (
              <Card title="活跃任务">
                <Table
                  dataSource={gpuTasks}
                  columns={processColumns.slice(0, -1)} // 移除命令列以节省空间
                  rowKey="process_id"
                  size="small"
                  pagination={false}
                />
              </Card>
            )}

            {/* 所有进程 */}
            <Card 
              title="所有进程"
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
                dataSource={tasks}
                columns={processColumns}
                rowKey="process_id"
                size="small"
                scroll={{ x: 1000 }}
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 条记录`
                }}
              />
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  )
}

export default GpuPage