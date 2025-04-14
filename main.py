from program.interface import run_cli

if __name__ == "__main__":
    def get_command(dict, gpu_id):
        return f"CUDA_VISIBLE_DEVICES={gpu_id} python test.py " + " ".join([f"--{key} {value}" for key, value in dict.items()])
    run_cli(get_command)