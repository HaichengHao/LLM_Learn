# @Time    : 2026/5/9 11:23
# @Author  : hero
# @File    : 07在线加载数据.py
# Hugging Face Hub 提供了大量开源数据集，涵盖文本分类、问答、翻译、摘要等任务，可以在官网浏览与搜索
from datasets import load_dataset

ds = load_dataset("SALT-NLP/SWE-chat", "conversations")

'''
执行上述代码时，数据集会自动从 Hugging Face Hub 下载，并缓存至本地用户目录，默认路径为：~/.cache/huggingface/datasets/
后续再次使用时将自动从本地加载，无需联网或重复下载。
加载完成后，返回一个 DatasetDict对象，结构和使用方式与本地数据完全一致'''