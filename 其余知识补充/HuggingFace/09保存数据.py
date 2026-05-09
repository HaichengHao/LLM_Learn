# @Time    : 2026/5/9 11:35
# @Author  : hero
# @File    : 09保存数据.py
'''
处理后的数据可保存到本地，供后续训练或复用，避免重复预处理。 Datasets提供了多种保存方式，适用于不同场景：
数据格式	保存方法	适用对象
Arrow	save_to_disk()	Dataset 或 DatasetDict
CSV	to_csv()	仅限 Dataset
JSON	to_json()	仅限 Dataset
'''


# 1 Arrow格式
# Arrow 格式是 Hugging Face 官方推荐的数据持久化方式，既支持单个 Dataset 也支持多个子集的DatasetDict

from datasets import load_dataset,load_from_disk

dataset = load_dataset('csv', './data/demo.csv')

dataset.save_to_disk('./data/processed')
'''
保存后的目录结构示例
processed/
├─ dataset_dict.json
├─ test/
│   ├─ data-00000-of-00001.arrow
│   ├─ dataset_info.json
│   └─ state.json
└─ train/
    ├─ data-00000-of-00001.arrow
    ├─ dataset_info.json
    └─ state.json'''

# tips:加载
dataset_dict = load_from_disk('./data/processed')



# 2 csv ,json格式


'''
如果希望将数据导出为通用格式（如用于可视化或非 Hugging Face 工具使用），可以使用 .to_csv() 或 .to_json()方法。
但需注意，这些方法仅适用于单个 Dataset，不支持 DatasetDict
'''

train_dataset = load_from_disk('./data/processed')

# csv
train_dataset.to_csv("./data/processed/train.csv")

# json
train_dataset.to_json("./data/processed/train.json")

# 加载
# 使用 load_dataset()，指定格式和路径即可重新加载
# 加载 CSV 文件
dataset_dict = load_dataset("csv", data_files="./data/processed/train.csv")

# 加载 JSON 文件
dataset_dict = load_dataset("json", data_files="./data/processed/train.json")

# 加载后返回一个结构完整的 DatasetDict，可直接用于训练、评估等任务。

