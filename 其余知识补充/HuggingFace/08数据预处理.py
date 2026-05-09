# @Time    : 2026/5/9 11:27
# @Author  : hero
# @File    : 08数据预处理.py



'''
除了加载数据， datasets库还支持常见的数据预处理操作，如编码文本、删除列、过滤样本、划分子集和设置张量格式。本节将逐步介绍这些功能
'''

from datasets import load_dataset
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer

dataset = load_dataset("SALT-NLP/SWE-chat", "conversations")

# 1 删除列
dataset = dataset.remove_columns(["label", "id"])


# 2 过滤行
dataset = dataset.filter(lambda x:x['review'] is not None and x['review'].strip()!="" and x['label'] in [0,1])

# 3 划分数据集
dataset_dict = dataset.train_test_split(test_size=0.2)
train_dataset, test_dataset = dataset_dict["train"],dataset_dict["test"]


# 4 编码数据

'''
可使用.map()方法与tokenizer配合，将原始文本批量编码为模型可用的输入格式（如 input_ids、attention_mask、token_type_ids等）。
.map()是 datasets 中的核心方法之一，支持对整个数据集中的每一条样本或每一批样本进行统一处理，常用于文本编码（tokenizer）和数据字段换。.map() 方法基本语法如下
'''

dataset = dataset.map(function,batched=False,remove_columns=None)
'''
参数说明如下：
参数	说明
function	要应用到每条样本上的函数（或每批样本上的函数）
batched	是否以“批”为单位处理样本；若为 True，则每次接收一个样本列表
remove_columns	是否删除原始列，常用于清理不再需要的字段
'''

# 以中文 BERT 模型为例，编码流程如下
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

def tokenize(example):
  encoded = tokenizer(
    example["review"],
    padding="max_length",
    truncation=True,
    max_length=128
  )
  example['input_ids'] = encoded['input_ids']
  example['attention_mask'] = encoded['attention_mask']
  
  return example

train_dataset = train_dataset.map(tokenize, batched=True)
test_dataset = test_dataset.map(tokenize, batched=True)

# 编码后，数据集中将新增字段如 input_ids 和 attention_mask，可直接用于模型训练。