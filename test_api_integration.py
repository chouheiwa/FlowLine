#!/usr/bin/env python3
"""
API集成测试脚本
测试新的任务管理功能
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5001/api"

def test_api_connection():
    """测试API连接"""
    try:
        response = requests.get(f"{API_BASE_URL}/system/info")
        if response.status_code == 200:
            print("✅ API连接成功")
            print(f"系统信息: {response.text}")
            return True
        else:
            print(f"❌ API连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接异常: {e}")
        return False

def test_gpu_info():
    """测试GPU信息获取"""
    try:
        response = requests.get(f"{API_BASE_URL}/gpus")
        if response.status_code == 200:
            gpu_data = response.json()
            print("✅ GPU信息获取成功")
            print(f"GPU数量: {len(gpu_data)}")
            for gpu_id, info in gpu_data.items():
                print(f"  GPU {gpu_id}: {info['name']} - {info['free_memory']:.0f}MB可用")
            return True
        else:
            print(f"❌ GPU信息获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GPU信息获取异常: {e}")
        return False

def test_task_creation():
    """测试任务创建"""
    try:
        task_data = {
            "name": "测试任务",
            "cmd": "echo 'Hello FlowLine'",
            "working_dir": "/tmp",
            "need_run_num": 1,
            "config_dict": {"test": "value"}
        }
        
        response = requests.post(f"{API_BASE_URL}/task/create", json=task_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                task_id = result.get('task_id')
                print(f"✅ 任务创建成功，任务ID: {task_id}")
                return task_id
            else:
                print(f"❌ 任务创建失败: {result.get('error')}")
                return None
        else:
            print(f"❌ 任务创建请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 任务创建异常: {e}")
        return None

def test_task_list():
    """测试任务列表获取"""
    try:
        response = requests.get(f"{API_BASE_URL}/task/list")
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ 任务列表获取成功，共{len(tasks)}个任务")
            for task_info in tasks:
                task_id = task_info.get('task_id', 'Unknown')
                task_name = task_info.get('name', 'Unknown')
                print(f"  任务 {task_id}: {task_name}")
            return tasks
        else:
            print(f"❌ 任务列表获取失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 任务列表获取异常: {e}")
        return None

def test_task_copy(original_task_id):
    """测试任务复制"""
    if not original_task_id:
        print("❌ 无法测试任务复制：没有原始任务ID")
        return None
        
    try:
        copy_data = {
            "original_task_id": original_task_id,
            "new_name": "复制的测试任务",
            "need_run_num": 2
        }
        
        response = requests.post(f"{API_BASE_URL}/task/copy", json=copy_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                new_task_id = result.get('new_task_id')
                print(f"✅ 任务复制成功，新任务ID: {new_task_id}")
                return new_task_id
            else:
                print(f"❌ 任务复制失败: {result.get('error')}")
                return None
        else:
            print(f"❌ 任务复制请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 任务复制异常: {e}")
        return None

def test_task_detail(task_id):
    """测试任务详情获取"""
    if not task_id:
        print("❌ 无法测试任务详情：没有任务ID")
        return None
        
    try:
        response = requests.get(f"{API_BASE_URL}/task/{task_id}")
        if response.status_code == 200:
            task_detail = response.json()
            print(f"✅ 任务详情获取成功")
            print(f"  任务名称: {task_detail.get('name', 'Unknown')}")
            print(f"  命令: {task_detail.get('cmd', 'Unknown')}")
            print(f"  工作目录: {task_detail.get('working_dir', 'Unknown')}")
            return task_detail
        else:
            print(f"❌ 任务详情获取失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 任务详情获取异常: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 开始FlowLine API集成测试")
    print("=" * 50)
    
    # 测试API连接
    if not test_api_connection():
        print("❌ API连接失败，终止测试")
        return
    
    print("\n" + "-" * 30)
    
    # 测试GPU信息
    test_gpu_info()
    
    print("\n" + "-" * 30)
    
    # 测试任务创建
    task_id = test_task_creation()
    
    print("\n" + "-" * 30)
    
    # 测试任务列表
    test_task_list()
    
    print("\n" + "-" * 30)
    
    # 测试任务详情
    test_task_detail(task_id)
    
    print("\n" + "-" * 30)
    
    # 测试任务复制
    new_task_id = test_task_copy(task_id)
    
    print("\n" + "-" * 30)
    
    # 再次测试任务列表以确认复制
    print("复制后的任务列表:")
    test_task_list()
    
    print("\n" + "=" * 50)
    print("🎉 FlowLine API集成测试完成！")

if __name__ == "__main__":
    main()