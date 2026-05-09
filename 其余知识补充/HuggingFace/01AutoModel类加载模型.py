# @Time    : 2026/5/7 18:16
# @Author  : hero
# @File    : 01AutoModel类加载模型.py

'''
AutoModel 会根据提供的模型名称，从 Hugging Face Hub 上下载所需的模型资源，包括模型权重和配置文件。
这些文件会自动缓存到本地，默认路径是：~/.cache/huggingface/hub/。下次加载相同模型时会直接读取缓存，不再联网下载。
如需使用国内镜像站，需配置如下环境变量
HF_ENDPOINT=https://hf-mirror.com
'''
from transformers import AutoModel
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
model = AutoModel.from_pretrained("google-bert/bert-base-chinese")  #TIPS：这个是在线加载


# 除了在线加载模型之外，from_pretrained()也支持从本地路径加载模型，要求目录中包含模型权重和配置文件，代码如下
model_local=AutoModel.from_pretrained('~/.cache/huggingface/hub/google-bert/bert-base-chinese')

