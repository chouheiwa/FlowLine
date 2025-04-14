import asyncio
import signal
import sys
from program import program


async def main():
    try:
        print("启动主处理循环...")
        # 启动主处理循环，但不等待它完成
        task = await program.run_process()
        
        print("程序已启动，按Ctrl+C终止...")
        
        # 保持程序运行直到收到中断信号
        while is_running:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"发生异常: {e}")
    finally:
        # 确保在退出前停止处理循环
        print("正在停止处理循环...")
        await program.stop_process()
        print("程序已安全终止")

if __name__ == "__main__":
    # 使用asyncio.run启动主程序
    asyncio.run(main())