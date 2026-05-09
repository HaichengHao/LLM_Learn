# @Time    : 2026/5/9 11:43
# @Author  : hero
# @File    : 10集成DataLoader.py
'''
经过预处理的datasets.Dataset对象可以直接与PyTorch的DataLoader集成使用。
虽然它并非继承自torch.utils.data.Dataset类，但由于实现了__len__()和__getitem__()这两个核心接口，因此能够被DataLoader正确识别并进行批量迭代。
在使用前，需要通过.set_format()方法将指定字段转换为张量格式以适配模型输入。典型配置如下
'''
from torch.utils.data import DataLoader
from datasets import load_dataset
train_dataset = load_dataset("csv", data_files="./data/processed/train.csv")


train_dataset.set_format(
  type="torch", # 指定输出为PyTorch张量
  columns=["input_ids", "attention_mask", "label"] # 需要转换的字段
)

'''
需要注意的是：
该方法仅改变通过__getitem__()（即dataset[i]）访问样本时的返回格式，不会修改底层数据存储
通过columns指定的字段会在访问时自动转换为torch.Tensor类型
未通过columns指定的字段在访问时将被自动过滤

'''

# 完成格式设置后，即可创建标准的DataLoader实例：

# 训练集DataLoader
train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)