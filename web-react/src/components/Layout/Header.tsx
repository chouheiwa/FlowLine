import React from 'react'
import { Layout, Typography, Space, Avatar } from 'antd'
import { UserOutlined } from '@ant-design/icons'

const { Header: AntHeader } = Layout
const { Title } = Typography

const Header: React.FC = () => {
  return (
    <AntHeader style={{ 
      background: '#fff', 
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
      padding: '0 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    }}>
      <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
        FlowLine
      </Title>
      
      <Space>
        <Avatar icon={<UserOutlined />} />
        <span>Admin</span>
      </Space>
    </AntHeader>
  )
}

export default Header