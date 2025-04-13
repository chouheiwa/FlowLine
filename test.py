
import time
import argparse
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--test', type=str, default='test', help='test')
    args = parser.parse_args()
    
    import torch

    print(torch.__version__)  # 检查PyTorch版本
    # 检查CUDA是否可用
    if torch.cuda.is_available():
        x = torch.randn(1000, 1000).to("cuda:2")
        y = x @ x
        print("CUDA is working!")
    else:
        print("CUDA is not available.")
    
    while True:
        print(time.time(),args.test)
        time.sleep(1)