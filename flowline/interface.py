import cmd
import sys

from .program import ProgramManager

class CommandLineInterface(cmd.Cmd):
    intro = '欢迎使用任务处理系统. 输入 help 或 ? 查看帮助.\n'
    prompt = '> '
    
    def __init__(self, program_manager):
        super().__init__()
        self.program_manager = program_manager
        
    def do_start(self, arg):
        """启动处理循环: start"""
        self.program_manager.start_process_loop()
        
    def do_stop(self, arg):
        """停止处理循环: stop"""
        self.program_manager.stop_process_loop()
        
    def do_switchrun(self, arg):
        """切换处理循环状态: switchrun"""
        is_running = self.program_manager.switch_run()
        print(f"处理循环现在{'正在运行' if is_running else '已停止'}")
        
    def do_switchgpu(self, arg):
        """切换GPU状态: gpu <id>"""
        try:
            gpu_id = int(arg.strip())
            self.program_manager.switch_gpu(gpu_id)
        except ValueError:
            print("错误: GPU ID必须是数字")
            
    def do_killgpu(self, arg):
        """终止指定GPU上的所有进程: killgpu <id>"""
        try:
            gpu_id = int(arg.strip())
            self.program_manager.kill_process_by_gpu(gpu_id)
        except ValueError:
            print("错误: GPU ID必须是数字")
            
    def do_kill(self, arg):
        """终止指定ID的进程: kill <id>"""
        try:
            process_id = int(arg.strip())
            self.program_manager.kill_process(process_id)
        except ValueError:
            print("错误: 进程ID必须是数字")
            
    def do_list(self, arg):
        """列出所有正在运行的进程: list"""
        self.program_manager.list_processes()
        
    def do_gpus(self, arg):
        """列出所有GPU状态: gpus"""
        self.program_manager.list_gpus()
        
    def do_exit(self, arg=None):
        """退出程序: exit"""
        print("正在清理资源...")
        self.program_manager.exit()
        print("再见!")
        return True
        
    def do_quit(self, arg):
        """退出程序: quit"""
        return self.do_exit(arg)
        
    def do_EOF(self, arg):
        """Ctrl+D退出程序"""
        print()  # 打印一个空行
        return self.do_exit(arg)
    
    def do_max(self, arg):
        """设置最大进程数: max <num>"""
        try:
            max_processes = int(arg.strip())
            self.program_manager.set_max_processes(max_processes)
        except ValueError:
            print("错误: 最大进程数必须是数字")

def run_cli(get_command):
    """启动命令行界面"""
    program = ProgramManager(get_command)
    cli = CommandLineInterface(program)
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n接收到中断信号，正在退出...")
        program.stop_process_loop()
        sys.exit(0)

if __name__ == "__main__":
    def get_command(dict, gpu_id):
        return f"CUDA_VISIBLE_DEVICES={gpu_id} python test.py " + " ".join([f"--{key} {value}" for key, value in dict.items()])
    run_cli(get_command)

"""
    python -m flowline.interface
"""  