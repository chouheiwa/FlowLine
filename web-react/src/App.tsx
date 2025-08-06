import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import { Header, Sidebar } from './components/Layout'
import { GpuPage, TasksPage, LogsPage, SettingsPage } from './pages'

const { Content } = Layout

function App() {
  return (
    <Layout>
      <Header />
      <Layout>
        <Sidebar />
        <Layout>
          <Content>
            <Routes>
              <Route path="/" element={<Navigate to="/gpu" replace />} />
              <Route path="/gpu" element={<GpuPage />} />
              <Route path="/tasks" element={<TasksPage />} />
              <Route path="/logs" element={<LogsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}

export default App