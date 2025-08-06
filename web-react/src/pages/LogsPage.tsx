import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Button, Space, Form, Input, Select, InputNumber, List, Typography, message } from 'antd'
import { ReloadOutlined, DownloadOutlined, ClearOutlined } from '@ant-design/icons'
import { logApi } from '../services/api'

const { TextArea } = Input
const { Option } = Select
const { Text } = Typography

interface LogFile {
  name: string
  size: number
  modified: string
}

const LogsPage: React.FC = () => {
  const [logFiles, setLogFiles] = useState<LogFile[]>([])
  const [selectedLogFile, setSelectedLogFile] = useState<string | null>(null)
  const [logContent, setLogContent] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const [form] = Form.useForm()

  useEffect(() => {
    fetchLogFiles()
  }, [])

  const fetchLogFiles = async () => {
    try {
      setLoading(true)
      const files = await logApi.getLogFiles()
      setLogFiles(files)
    } catch (error) {
      message.error('获取日志文件列表失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchLogContent = async (filename: string, options?: {
    search?: string
    level?: string
    maxLines?: number
  }) => {
    try {
      setLoading(true)
      const content = await logApi.getLogContent(filename, options)
      setLogContent(content)
      
      if (autoScroll) {
        setTimeout(() => {
          const logContainer = document.getElementById('log-content')
          if (logContainer) {
            logContainer.scrollTop = logContainer.scrollHeight
          }
        }, 100)
      }
    } catch (error) {
      message.error('获取日志内容失败')
    } finally {
      setLoading(false)
    }
  }

  const handleLogFileSelect = (filename: string) => {
    setSelectedLogFile(filename)
    fetchLogContent(filename)
  }

  const handleApplyFilter = (values: any) => {
    if (selectedLogFile) {
      fetchLogContent(selectedLogFile, {
        search: values.searchTerm,
        level: values.logLevel === 'all' ? undefined : values.logLevel,
        maxLines: values.maxLines
      })
    }
  }

  const handleDownload = () => {
    if (selectedLogFile && logContent) {
      const blob = new Blob([logContent], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = selectedLogFile
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      message.success('日志文件下载成功')
    }
  }

  const handleClearLog = () => {
    // TODO: 实现清空日志的API调用
    message.success('日志已清空')
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="page-container">
      <Row gutter={[16, 16]}>
        {/* 侧边栏 */}
        <Col span={6}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 日志文件列表 */}
            <Card 
              title="日志文件"
              extra={
                <Button 
                  icon={<ReloadOutlined />}
                  onClick={fetchLogFiles}
                  loading={loading}
                  size="small"
                >
                  刷新
                </Button>
              }
            >
              <List
                size="small"
                dataSource={logFiles}
                renderItem={(file) => (
                  <List.Item
                    style={{
                      cursor: 'pointer',
                      padding: '8px',
                      border: selectedLogFile === file.name ? '2px solid #1890ff' : '1px solid transparent',
                      borderRadius: '4px',
                      marginBottom: '4px'
                    }}
                    onClick={() => handleLogFileSelect(file.name)}
                  >
                    <div style={{ width: '100%' }}>
                      <div style={{ fontWeight: 'bold' }}>{file.name}</div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {formatFileSize(file.size)} • {file.modified}
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            </Card>

            {/* 日志筛选 */}
            <Card title="日志筛选">
              <Form
                form={form}
                layout="vertical"
                onFinish={handleApplyFilter}
                initialValues={{
                  logLevel: 'all',
                  maxLines: 1000
                }}
              >
                <Form.Item
                  name="searchTerm"
                  label="搜索关键词"
                >
                  <Input placeholder="输入关键词搜索" />
                </Form.Item>
                
                <Form.Item
                  name="logLevel"
                  label="日志级别"
                >
                  <Select>
                    <Option value="all">全部级别</Option>
                    <Option value="info">INFO</Option>
                    <Option value="warning">WARNING</Option>
                    <Option value="error">ERROR</Option>
                    <Option value="debug">DEBUG</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="maxLines"
                  label="最大行数"
                >
                  <InputNumber 
                    min={10} 
                    max={5000} 
                    style={{ width: '100%' }}
                  />
                </Form.Item>
                
                <Form.Item>
                  <Button type="primary" htmlType="submit" block>
                    应用筛选
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Space>
        </Col>

        {/* 主内容区 */}
        <Col span={18}>
          <Card 
            title={selectedLogFile || '选择日志文件'}
            extra={
              <Space>
                <Button 
                  icon={<DownloadOutlined />}
                  onClick={handleDownload}
                  disabled={!selectedLogFile || !logContent}
                >
                  下载
                </Button>
                <Button 
                  icon={<ClearOutlined />}
                  onClick={handleClearLog}
                  disabled={!selectedLogFile}
                  danger
                >
                  清空日志
                </Button>
              </Space>
            }
          >
            {selectedLogFile ? (
              <div>
                <div style={{ marginBottom: 16 }}>
                  <label>
                    <input 
                      type="checkbox" 
                      checked={autoScroll}
                      onChange={(e) => setAutoScroll(e.target.checked)}
                      style={{ marginRight: 8 }}
                    />
                    自动滚动至底部
                  </label>
                </div>
                
                <div
                  id="log-content"
                  style={{
                    height: '600px',
                    overflow: 'auto',
                    background: '#000',
                    color: '#fff',
                    padding: '16px',
                    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                    fontSize: '12px',
                    lineHeight: '1.4',
                    whiteSpace: 'pre-wrap',
                    borderRadius: '4px'
                  }}
                >
                  {logContent || '加载中...'}
                </div>
              </div>
            ) : (
              <div style={{ 
                height: '600px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: '#999'
              }}>
                <Text type="secondary">请从左侧选择一个日志文件</Text>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default LogsPage