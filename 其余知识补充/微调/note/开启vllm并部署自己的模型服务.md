## 模型训练在llama-factory完成之后配置检查点测试,测试完毕后指定一个路径参数合并导出
## 安装
```shell
uv pip install vllm -i https://pypi.tuna.tsinghua.edu.cn/simple
```
环境问题一直是难以避开的问题,这是需要的配置,并且最好是和llama-factory下的虚拟环境保持一致
```shell

uv pip uninstall torch torchvision torchaudio  #先清除掉旧的cpu版本

(vllmserver) nikofox@MOSS:~/llamafactory/vllmserver$ uv pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124

```
用下面这个检查
```shell
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'显卡: {torch.cuda.get_device_name(0)}')"

(vllmserver) nikofox@MOSS:~/llamafactory/vllmserver$ python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'PyTorch编译版本: {torch.version.cuda}'); print(f'显卡名称: {torch.cuda.get_device_name(0)}')"
CUDA可用: True
PyTorch编译版本: 12.4
显卡名称: NVIDIA GeForce RTX 2080 Ti

```




```shell
nikofox@MOSS:~/llamafactory/vllmserver$ uv pip install vllm -i https://pypi.tuna.tsinghua.edu.cn/simple
Resolved 180 packages in 15.08s
Prepared 75 packages in 54.32s
Installed 180 packages in 163ms
 + aiohappyeyeballs==2.6.1
 + aiohttp==3.13.5
 .
 .
 .
 .
 + zipp==3.23.1
nikofox@MOSS:~/llamafactory/vllmserver$ ls
nikofox@MOSS:~/llamafactory/vllmserver$ cd ..
nikofox@MOSS:~/llamafactory$ ls
LLaMA-Factory  vllmserver
nikofox@MOSS:~/llamafactory$ cd vllmserver/

nikofox@MOSS:~/llamafactory/vllmserver$ rsync -r ../LLaMA-Factory/model/Qwen3-0.6B/ ./Qwen3-0.6B  
nikofox@MOSS:~/llamafactory/vllmserver$ ls
Qwen3-0.6B
nikofox@MOSS:~/llamafactory/vllmserver$ cd Qwen3-0.6B/
nikofox@MOSS:~/llamafactory/vllmserver/Qwen3-0.6B$ ls
config.json             LICENSE            README.md              vocab.json
configuration.json      merges.txt         tokenizer_config.json
generation_config.json  model.safetensors  tokenizer.json
nikofox@MOSS:~/llamafactory/vllmserver/Qwen3-0.6B$ cd ..
nikofox@MOSS:~/llamafactory/vllmserver$ rsync -r ../LLaMA-Factory/saves/Custom/lora/qwen3-lora/full_params/ ./Qwen3-0.6B-sft-lora/
nikofox@MOSS:~/llamafactory/vllmserver$ ls
Qwen3-0.6B  Qwen3-0.6B-sft-lora
nikofox@MOSS:~/llamafactory/vllmserver$ cd Qwen3-0.6B
nikofox@MOSS:~/llamafactory/vllmserver/Qwen3-0.6B$ cd ..
nikofox@MOSS:~/llamafactory/vllmserver$ cd Qwen3-0.6B-sft-lora/
nikofox@MOSS:~/llamafactory/vllmserver/Qwen3-0.6B-sft-lora$ ls
chat_template.jinja     Modelfile              tokenizer.json
config.json             model.safetensors
generation_config.json  tokenizer_config.json
nikofox@MOSS:~/llamafactory/vllmserver/Qwen3-0.6B-sft-lora$ pwd
/home/nikofox/llamafactory/vllmserver/Qwen3-0.6B-sft-lora
nikofox@MOSS:~/llamafactory/vllmserver/Qwen3-0.6B-sft-lora$ cd ..
nikofox@MOSS:~/llamafactory/vllmserver$ pwd
/home/nikofox/llamafactory/vllmserver

(vllmserver) nikofox@MOSS:~/llamafactory/vllmserver$ vllm serve /home/nikofox/llamafactory/vllmserver/Qwen3-0.6B-sft-lora \
> --served-model-name Qwen3-0.6B-sft-lora \
> --tokenizer /home/nikofox/llamafactory/vllmserver/Qwen3-0.6B\
> --max-model-len 32768
usage: vllm [-h] [-v]
            {chat,complete,serve,launch,bench,collect-env,run-batch} ...
vllm: error: unrecognized arguments: 32768
(vllmserver) nikofox@MOSS:~/llamafactory/vllmserver$ vllm serve /home/nikofox/llamafactory/vllmserver/Qwen3-0.6B-sft-lora --served-model-name Qwen3-0.6B-sft-lora --tokenizer /home/nikofox/llamafactory/vllmserver/Qwen3-0.6B--max-model-len 32K
usage: vllm [-h] [-v]
            {chat,complete,serve,launch,bench,collect-env,run-batch} ...
vllm: error: unrecognized arguments: 32K
(vllmserver) nikofox@MOSS:~/llamafactory/vllmserver$ vllm serve /home/nikofox/llamafactory/vllmserver/Qwen3-0.6B-sft-lora \
--served-model-name Qwen3-0.6B-sft-lora \
--tokenizer /home/nikofox/llamafactory/vllmserver/Qwen3-0.6B \
--max-model-len 32768 \
--gpu-memory-utilization 0.9 \
--host 127.0.0.1 \
--port 5888
(APIServer pid=115478) INFO 05-02 20:35:33 [utils.py:299] 
(APIServer pid=115478) INFO 05-02 20:35:33 [utils.py:299]        █     █     █▄   ▄█
(APIServer pid=115478) INFO 05-02 20:35:33 [utils.py:299]  ▄▄ ▄█ █     █     █ ▀▄▀ █  version 0.20.0
(APIServer pid=115478) INFO 05-02 20:35:33 [utils.py:299]   █▄█▀ █     █     █     █  model   /home/nikofox/llamafactory/vllmserver/Qwen3-0.6B-sft-lora
(APIServer pid=115478) INFO 05-02 20:35:33 [utils.py:299]    ▀▀  ▀▀▀▀▀ ▀▀▀▀▀ ▀     ▀
(APIServer pid=115478) INFO 05-02 20:35:33 [utils.py:299] 
(APIServer pid=115478) INFO 05-02 20:35:33 [utils.py:233] non-default args: {'model_tag': '/home/nikofox/llamafactory/vllmserver/Qwen3-0.6B-sft-lora', 'host': '127.0.0.1', 'port': 5888, 'model': '/home/nikofox/llamafactory/vllmserver/Qwen3-0.6B-sft-lora', 'tokenizer': '/home/nikofox/llamafactory/vllmserver/Qwen3-0.6B', 'max_model_len': 32768, 'served_model_name': ['Qwen3-0.6B-sft-lora'], 'gpu_memory_utilization': 0.9}

```