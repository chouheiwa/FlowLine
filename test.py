
import time
import argparse
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--test', type=str, default='test', help='test')
    parser.add_argument('--gpu', type=int, default=0, help='gpu')
    parser.add_argument('--data_name', type=str, default='test', help='data_name')
    parser.add_argument('--model_name', type=str, default='test', help='model_name')
    parser.add_argument('--method_name', type=str, default='test', help='method_name')
    parser.add_argument('--domain_num', type=int, default=1, help='domain_num')
    parser.add_argument('--seed', type=int, default=1, help='seed')
    args = parser.parse_args()
    
    import torch

    print(torch.__version__)  # 检查PyTorch版本
    # 检查CUDA是否可用
    if torch.cuda.is_available():
        x = torch.randn(1000, 1000).to("cuda")
        y = x @ x
        print("CUDA is working!")
    else:
        print("CUDA is not available.")
    
    while True:
        print(time.time(),args.test)
        time.sleep(1)