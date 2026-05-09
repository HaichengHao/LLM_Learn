# @Time    : 2026/5/9 00:46
# @Author  : hero
# @File    : 06load_datasets加载本地数据.py
from datasets import load_dataset

# dataset=load_dataset(format,data_files=路径或字典)

'''
参数	类型	说明
format	str	文件格式，常用的包括 "csv"、"json"、"parquet" 等
data_files	str 或 dict	文件路径。可传入字符串（加载单个文件）或字典（加载多个文件，如训练数据/测试数据）
'''

# 加载多个文件
dataset_dict = load_dataset('csv', data_files={
  'train': './data/train.csv',
  'test': './data/test.csv'
})
# tips:此时返回的是一个包含两个Dataset的 DatasetDict，其中每个Dataset称为一个split。
print(dataset_dict)
# DatasetDict({
#   train: Dataset(...),
#   test: Dataset(...)
# })



# 加载单个文件
dataset_dict = load_dataset('csv', data_files='./data/dataset.csv')
# 此时返回的也是一个 DatasetDict，其中只包含默认命名为 "train" 的一个Dataset。
print(dataset_dict)
# DatasetDict({
#   train: Dataset(...)
# })


#查看数据集
dataset_dict = load_dataset('csv', data_files='data/raw/online_shopping_10_cats.csv')
dataset = dataset_dict["train"]

# 此时 dataset是一个 `Dataset` 对象，表示训练集

#tips:访问样本
# Dataset支持索引和切片操作来访问样本

print(dataset[0])    # 单条样本
print(dataset[:3])   # 多条样本（注意返回结构）

'''
访问方式	返回示例
dataset[0]	{'review': '很喜欢的一本书', 'label': 1, 'cat': '书籍'}
dataset[:3]	{'review': ['很喜欢的一本书', '内容丰富', '讲解清晰'], 'label': [1, 1, 1], 'cat': ['书籍','书籍','书籍']}'''

# 访问某个字段值
# 可以进一步通过字段名访问某个字段的值：

print(dataset[0]['review'])    # 第一条样本的 review 字段
print(dataset[:3]['review'])    # 前三条样本的 review 字段列表