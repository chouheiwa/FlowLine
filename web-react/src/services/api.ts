import axios from 'axios'
import { GpuInfo, TaskInfo } from '../types'

const API_BASE_URL = `/api`

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

// GPU相关API
export const gpuApi = {
  // 获取所有GPU信息
  getGpus: async (): Promise<GpuInfo[]> => {
    const response = await api.get('/gpus')
    const gpuObject = response.data
    
    const gpuData: GpuInfo[] = []
    for (const gpu_id in gpuObject) {
      if (gpuObject.hasOwnProperty(gpu_id)) {
        const gpu = gpuObject[gpu_id]
        gpuData.push({
          gpu_id: gpu_id,
          name: gpu.name,
          status: gpu.status,
          memory: {
            used: ((gpu.total_memory - gpu.free_memory) / 1024).toFixed(1),
            free: (gpu.free_memory / 1024).toFixed(1),
            total: (gpu.total_memory / 1024).toFixed(1)
          },
          utilization: gpu.utilization,
          temperature: gpu.temperature,
          power: {
            current: gpu.power,
            max: gpu.max_power
          }
        })
      }
    }
    return gpuData
  },

  // 获取特定GPU的任务
  getGpuTasks: async (gpuId: string): Promise<TaskInfo[]> => {
    const response = await api.get(`/gpu/${gpuId}/process`)
    const taskObject = response.data
    
    const tasks: TaskInfo[] = []
    for (const task_id in taskObject) {
      if (taskObject.hasOwnProperty(task_id)) {
        const task = taskObject[task_id]
        const now = new Date()
        const startTime = task.start_time ? new Date(task.start_time * 1000) : new Date()
        const runTime = Math.floor((now.getTime() - startTime.getTime()) / 60000)
        
        tasks.push({
          process_id: task_id,
          task_id: task.task_id,
          pid: task.pid,
          status: task.status.toLowerCase(),
          gpu_id: task.gpu_id.toString(),
          user: "user",
          command: task.func,
          startTime: startTime.toLocaleString(),
          runTime: `${runTime} 分钟`
        })
      }
    }
    return tasks
  }
}

// 进程相关API
export const processApi = {
  // 获取所有进程
  getProcesses: async (): Promise<TaskInfo[]> => {
    const response = await api.get('/process')
    const processObject = response.data
    
    const taskData: TaskInfo[] = []
    for (const process_id in processObject) {
      if (processObject.hasOwnProperty(process_id)) {
        const process = processObject[process_id]
        const now = new Date()
        const startTime = process.start_time ? new Date(process.start_time * 1000) : new Date()
        const runTime = Math.floor((now.getTime() - startTime.getTime()) / 60000)
        
        taskData.push({
          process_id: process_id,
          task_id: process.task_id,
          pid: process.pid,
          status: process.status.toLowerCase(),
          gpu_id: process.gpu_id.toString(),
          user: "user",
          command: process.func,
          startTime: startTime.toLocaleString(),
          runTime: `${runTime} 分钟`
        })
      }
    }
    return taskData
  }
}

// 系统控制API
export const systemApi = {
  // 运行/停止系统
  toggleRun: async (): Promise<{ if_run: boolean }> => {
    const response = await api.post('/run')
    return response.data
  }
}

// 任务相关API
export const taskApi = {
  // 创建任务
  createTask: async (taskData: { name: string; command: string }) => {
    const response = await api.post('/tasks', taskData)
    return response.data
  },

  // 删除任务
  deleteTask: async (taskId: string) => {
    const response = await api.delete(`/tasks/${taskId}`)
    return response.data
  }
}

// 日志相关API
export const logApi = {
  // 获取日志文件列表
  getLogFiles: async () => {
    const response = await api.get('/logs')
    return response.data
  },

  // 获取日志内容
  getLogContent: async (filename: string, options?: { 
    search?: string
    level?: string
    maxLines?: number
  }) => {
    const params = new URLSearchParams()
    if (options?.search) params.append('search', options.search)
    if (options?.level) params.append('level', options.level)
    if (options?.maxLines) params.append('maxLines', options.maxLines.toString())
    
    const response = await api.get(`/logs/${filename}?${params}`)
    return response.data
  }
}

export default api