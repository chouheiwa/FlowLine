from flowline.api_test import get_app

def get_command(dict, gpu_id):
    return f"CUDA_VISIBLE_DEVICES={gpu_id} python test.py " + " ".join([f"--{key} {value}" for key, value in dict.items()])

if __name__ == '__main__':
    app = get_app(get_command)
    app.run(host='0.0.0.0', port=5000, debug=True)