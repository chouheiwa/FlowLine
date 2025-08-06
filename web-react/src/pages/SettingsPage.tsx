import React, { useState } from 'react'
import { Card, Tabs, Form, Input, Select, InputNumber, Switch, Button, Space, message, Row, Col } from 'antd'
import { SaveOutlined } from '@ant-design/icons'
import { useAppStore } from '../store'

const { Option } = Select
const { TextArea } = Input

const SettingsPage: React.FC = () => {
  const { settings, updateSettings } = useAppStore()
  const [activeTab, setActiveTab] = useState('general')
  const [generalForm] = Form.useForm()
  const [gpuForm] = Form.useForm()
  const [tasksForm] = Form.useForm()
  const [logsForm] = Form.useForm()

  const handleSaveGeneral = (values: any) => {
    updateSettings({ general: values })
    message.success('通用设置保存成功')
  }

  const handleSaveGpu = (values: any) => {
    updateSettings({ gpu: values })
    message.success('GPU设置保存成功')
  }

  const handleSaveTasks = (values: any) => {
    updateSettings({ tasks: values })
    message.success('任务设置保存成功')
  }

  const handleSaveLogs = (values: any) => {
    updateSettings({ logs: values })
    message.success('日志设置保存成功')
  }

  const tabItems = [
    {
      key: 'general',
      label: '通用设置',
      children: (
        <Card>
          <Form
            form={generalForm}
            layout="vertical"
            initialValues={settings.general}
            onFinish={handleSaveGeneral}
          >
            <Row gutter={16}>
              <Col span={12}>
                <h3>应用程序设置</h3>
                
                <Form.Item
                  name="appName"
                  label="应用名称"
                  rules={[{ required: true, message: '请输入应用名称' }]}
                >
                  <Input />
                </Form.Item>
                
                <Form.Item
                  name="language"
                  label="界面语言"
                >
                  <Select>
                    <Option value="zh-CN">简体中文</Option>
                    <Option value="en-US" disabled>English（暂不可用）</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="theme"
                  label="界面主题"
                >
                  <Select>
                    <Option value="light">浅色主题</Option>
                    <Option value="dark" disabled>深色主题（暂不可用）</Option>
                    <Option value="system" disabled>跟随系统（暂不可用）</Option>
                  </Select>
                </Form.Item>
              </Col>
              
              <Col span={12}>
                <h3>数据设置</h3>
                
                <Form.Item
                  name="dataDir"
                  label="数据目录"
                >
                  <Input disabled />
                </Form.Item>
                
                <Form.Item
                  name="backupInterval"
                  label="自动备份间隔 (小时)"
                >
                  <InputNumber min={1} max={168} disabled />
                </Form.Item>
                
                <Form.Item
                  name="autoCleanup"
                  label="自动清理过期数据"
                  valuePropName="checked"
                >
                  <Switch disabled />
                </Form.Item>
              </Col>
            </Row>
            
            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                保存设置
              </Button>
            </Form.Item>
          </Form>
        </Card>
      )
    },
    {
      key: 'gpu',
      label: 'GPU设置',
      children: (
        <Card>
          <Form
            form={gpuForm}
            layout="vertical"
            initialValues={settings.gpu}
            onFinish={handleSaveGpu}
          >
            <Row gutter={16}>
              <Col span={12}>
                <h3>GPU 监控设置</h3>
                
                <Form.Item
                  name="refreshInterval"
                  label="刷新间隔 (秒)"
                  rules={[{ required: true, message: '请输入刷新间隔' }]}
                >
                  <InputNumber min={1} max={60} />
                </Form.Item>
                
                <Form.Item
                  name="temperatureUnit"
                  label="温度单位"
                >
                  <Select>
                    <Option value="celsius">摄氏度 (°C)</Option>
                    <Option value="fahrenheit">华氏度 (°F)</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="autoDetect"
                  label="自动检测GPU"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
              
              <Col span={12}>
                <h3>GPU 性能阈值</h3>
                
                <Form.Item
                  name="maxTemperature"
                  label="最高温度警告 (°C)"
                  rules={[{ required: true, message: '请输入最高温度' }]}
                >
                  <InputNumber min={60} max={110} />
                </Form.Item>
                
                <Form.Item
                  name="maxUtilization"
                  label="最高利用率警告 (%)"
                  rules={[{ required: true, message: '请输入最高利用率' }]}
                >
                  <InputNumber min={50} max={100} />
                </Form.Item>
                
                <Form.Item
                  name="maxMemoryUsage"
                  label="最高内存使用警告 (%)"
                  rules={[{ required: true, message: '请输入最高内存使用率' }]}
                >
                  <InputNumber min={50} max={100} />
                </Form.Item>
              </Col>
            </Row>
            
            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                保存设置
              </Button>
            </Form.Item>
          </Form>
        </Card>
      )
    },
    {
      key: 'tasks',
      label: '任务设置',
      children: (
        <Card>
          <Form
            form={tasksForm}
            layout="vertical"
            initialValues={settings.tasks}
            onFinish={handleSaveTasks}
          >
            <h3>任务执行设置</h3>
            
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="maxConcurrentTasks"
                  label="最大并发任务数"
                  rules={[{ required: true, message: '请输入最大并发任务数' }]}
                >
                  <InputNumber min={1} max={32} />
                </Form.Item>
                
                <Form.Item
                  name="taskTimeoutHours"
                  label="默认任务超时时间 (小时)"
                  rules={[{ required: true, message: '请输入任务超时时间' }]}
                >
                  <InputNumber min={1} max={168} />
                </Form.Item>
              </Col>
              
              <Col span={12}>
                <Form.Item
                  name="autoRetry"
                  label="失败任务自动重试"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
            </Row>
            
            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                保存设置
              </Button>
            </Form.Item>
          </Form>
        </Card>
      )
    },
    {
      key: 'logs',
      label: '日志设置',
      children: (
        <Card>
          <Form
            form={logsForm}
            layout="vertical"
            initialValues={settings.logs}
            onFinish={handleSaveLogs}
          >
            <h3>日志管理设置</h3>
            
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="maxLogSize"
                  label="最大日志文件大小 (MB)"
                  rules={[{ required: true, message: '请输入最大日志文件大小' }]}
                >
                  <InputNumber min={1} max={1000} />
                </Form.Item>
                
                <Form.Item
                  name="logLevel"
                  label="日志级别"
                >
                  <Select>
                    <Option value="debug">DEBUG</Option>
                    <Option value="info">INFO</Option>
                    <Option value="warning">WARNING</Option>
                    <Option value="error">ERROR</Option>
                  </Select>
                </Form.Item>
              </Col>
              
              <Col span={12}>
                <Form.Item
                  name="autoRotate"
                  label="自动轮转日志"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
            </Row>
            
            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                保存设置
              </Button>
            </Form.Item>
          </Form>
        </Card>
      )
    },
    {
      key: 'about',
      label: '关于',
      children: (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <h1 style={{ color: '#1890ff', marginBottom: '16px' }}>FlowLine</h1>
            <p style={{ fontSize: '16px', marginBottom: '8px' }}>GPU管理系统</p>
            <p style={{ color: '#666', marginBottom: '24px' }}>版本 1.0.0</p>
            
            <div style={{ textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
              <h3>功能特性</h3>
              <ul>
                <li>实时GPU监控和状态显示</li>
                <li>任务管理和调度</li>
                <li>日志查看和分析</li>
                <li>系统设置和配置</li>
              </ul>
              
              <h3>技术栈</h3>
              <ul>
                <li>前端：React + Ant Design + TypeScript</li>
                <li>状态管理：Zustand</li>
                <li>路由：React Router</li>
                <li>构建工具：Vite</li>
              </ul>
            </div>
          </div>
        </Card>
      )
    }
  ]

  return (
    <div className="page-container">
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
        tabPosition="left"
        style={{ minHeight: '600px' }}
      />
    </div>
  )
}

export default SettingsPage