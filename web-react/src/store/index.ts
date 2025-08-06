import { create } from 'zustand'
import { GpuInfo, TaskInfo, Settings } from '../types'
import { gpuApi, processApi, systemApi, taskApi } from '../services/api'

interface AppState {
  // GPU相关状态
  gpus: GpuInfo[]
  selectedGpuId: string | null
  gpuTasks: TaskInfo[]
  
  // 任务相关状态
  tasks: TaskInfo[]
  
  // 系统状态
  isRunning: boolean
  loading: boolean
  
  // 设置
  settings: Settings
  
  // Actions
  fetchGpus: () => Promise<void>
  fetchTasks: () => Promise<void>
  fetchGpuTasks: (gpuId: string) => Promise<void>
  selectGpu: (gpuId: string | null) => void
  toggleSystem: () => Promise<void>
  setLoading: (loading: boolean) => void
  updateSettings: (settings: Partial<Settings>) => void
}

const defaultSettings: Settings = {
  general: {
    appName: 'FlowLine',
    language: 'zh-CN',
    theme: 'light',
    dataDir: '/home/me/flowline/data',
    backupInterval: 24,
    autoCleanup: true
  },
  gpu: {
    refreshInterval: 5,
    temperatureUnit: 'celsius',
    autoDetect: true,
    maxTemperature: 85,
    maxUtilization: 95,
    maxMemoryUsage: 90
  },
  tasks: {
    maxConcurrentTasks: 4,
    taskTimeoutHours: 24,
    autoRetry: true
  },
  logs: {
    maxLogSize: 100,
    logLevel: 'info',
    autoRotate: true
  }
}

export const useAppStore = create<AppState>((set, get) => ({
  // 初始状态
  gpus: [],
  selectedGpuId: null,
  gpuTasks: [],
  tasks: [],
  isRunning: false,
  loading: false,
  settings: defaultSettings,

  // Actions
  fetchGpus: async () => {
    try {
      set({ loading: true })
      const gpus = await gpuApi.getGpus()
      set({ gpus, loading: false })
    } catch (error) {
      console.error('Failed to fetch GPUs:', error)
      set({ loading: false })
    }
  },

  fetchTasks: async () => {
    try {
      const tasks = await taskApi.getTasks()
      set({ tasks })
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    }
  },

  fetchGpuTasks: async (gpuId: string) => {
    try {
      const gpuTasks = await gpuApi.getGpuTasks(gpuId)
      set({ gpuTasks })
    } catch (error) {
      console.error('Failed to fetch GPU tasks:', error)
    }
  },

  selectGpu: (gpuId: string | null) => {
    set({ selectedGpuId: gpuId })
    if (gpuId) {
      get().fetchGpuTasks(gpuId)
    } else {
      set({ gpuTasks: [] })
    }
  },

  toggleSystem: async () => {
    try {
      const result = await systemApi.toggleRun()
      set({ isRunning: result.if_run })
    } catch (error) {
      console.error('Failed to toggle system:', error)
    }
  },

  setLoading: (loading: boolean) => {
    set({ loading })
  },

  updateSettings: (newSettings: Partial<Settings>) => {
    set(state => ({
      settings: {
        ...state.settings,
        ...newSettings
      }
    }))
  }
}))

export default useAppStore