export interface GpuInfo {
  gpu_id: string
  name: string
  status: string
  memory: {
    used: string
    free: string
    total: string
  }
  utilization: number
  temperature: number
  power: {
    current: number
    max: number
  }
}

export interface TaskInfo {
  process_id: string
  task_id: string
  pid: number
  status: string
  gpu_id: string
  user: string
  command: string
  startTime: string
  runTime: string
  working_dir?: string
  name?: string
  need_run_num?: number
  run_num?: number
  config_dict?: Record<string, any>
}

export interface CreateTaskRequest {
  name: string
  cmd: string
  working_dir?: string
  need_run_num?: number
  config_dict?: Record<string, any>
}

export interface CopyTaskRequest {
  original_task_id: number
  new_name: string
  need_run_num: number
}

export interface LogFile {
  name: string
  size: number
  modified: string
}

export interface Settings {
  general: {
    appName: string
    language: string
    theme: string
    dataDir: string
    backupInterval: number
    autoCleanup: boolean
  }
  gpu: {
    refreshInterval: number
    temperatureUnit: string
    autoDetect: boolean
    maxTemperature: number
    maxUtilization: number
    maxMemoryUsage: number
  }
  tasks: {
    maxConcurrentTasks: number
    taskTimeoutHours: number
    autoRetry: boolean
  }
  logs: {
    maxLogSize: number
    logLevel: string
    autoRotate: boolean
  }
}