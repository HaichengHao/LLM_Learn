# @Time    : 2026/5/7 18:25
# @Author  : hero
# @File    : 03Tokenizer的加载和使用.py
'''
在Transformers库中，AutoTokenizer用于加载与指定模型配套的分词器。
它会根据模型名称自动选择并实例化正确的分词器类型
（如 BertTokenizer、GPT2Tokenizer、T5Tokenizer 等）。
'''

from transformers import AutoTokenizer
import os
import torch

os.environ['HF_ENDPOINT']='https://hf-mirror.com'
#加载分词器具

tokenizer=AutoTokenizer.from_pretrained('google-bert/bert-base-chinese')


'''
AutoTokenizer 会根据提供的模型名称，从 Hugging Face Hub 上下载所需的文件资源，
包括配置文件词表。这些文件会自动缓存到本地，默认路径是：~/.cache/huggingface/hub/。
下次加载相同模型时会直接读取缓存，不再联网下载
之后AutoTokenizer便会根据配置文件和词表实例化一个Tokenizer对象。
'''


# tips:常用API

# 1 分词

tokens = tokenizer.tokenize('天空好像下雨,我好想住你隔壁')

print(tokens)



# 2 token 转ID(.convert_tokens_to_ids())

ids=tokenizer.convert_tokens_to_ids(tokens)
print(ids)

# 3 ID转token (.convert_ids_to_tokens)

tokens=tokenizer.tokenize("天空好像下雨")

print(tokens)

'''
['天', '空', '好', '像', '下', '雨', ',', '我', '好', '想', '住', '你', '隔', '壁']
[1921, 4958, 1962, 1008, 678, 7433, 117, 2769, 1962, 2682, 857, 872, 7392, 1880]
['天', '空', '好', '像', '下', '雨']
'''


#important: tokenizer() 方法（即 __call__）
# 这是最推荐的接口，用于直接构造模型所需的输入，其基本用法如下

tokenizer = AutoTokenizer.from_pretrained("./pretrained/bert-base-chinese")
text = "我爱自然语言处理"

# 编码文本为模型输入格式
inputs = tokenizer(text)

print(inputs)

'''
{
'input_ids': [101, 2769, 4263, 5632, 4197, 6427, 6241, 1905, 4415, 102], 
'token_type_ids': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
'attention_mask': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
}'''


# 除去text，tokenizer还提供了多个重要参数
texts = ["我爱自然语言处理", "我爱人工智能", "我们一起学习"]
inputs = tokenizer(
  texts,
  padding="max_length", # 自动补齐
  truncation=True, # 自动截断
  max_length=10, # 统一最大长度
  return_tensors="pt" # 返回 PyTorch 张量格式
)

print(inputs)

# 输出内容是一个包含三个字段的字典，每个字段是形状为 (batch_size, seq_len) 的张量
'''
{
	'input_ids': tensor([[ 101, 2769, 4263, 5632, 4197, 6427, 6241, 1905, 4415,  102],
                        [ 101, 2769, 4263,  782, 2339, 3255, 5543,  102,    0,    0],
                        [ 101, 2769,  812,  671, 6629, 2110,  739,  102,    0,    0]]), 
	'token_type_ids': tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]), 
	'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0]])
}'''

