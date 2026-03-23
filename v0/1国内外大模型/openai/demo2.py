#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：LLM 
@File    ：demo2.py
@IDE     ：PyCharm 
@Author  ：百年
@Date    ：2026/3/20 15:39 
'''

# 需求:1,创建一个向量空间 2,根据指定的关键字(词、句)去向量空间中作相似搜索(根据语义)

from openai import OpenAI
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
base_url = os.getenv('base_url')
api_key = os.getenv('api_key')
df = pd.read_csv('./datas/fine_food_reviews_1k.csv', index_col=0)  # tips:抛弃默认列索引

# tips:要除了anoymous列的所有列
df = df[df.columns.tolist()[1:]]
# tips:数据清洗
df = df.dropna()

# tips:数据合并,合并最后两个字段
df['text_content'] = 'Summary:' + df.Summary.str.strip() + '; Text: ' + df.Text.str.strip()

print(df)

# step 进行向量化

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)


def text2vec(text, model_name):
    return client.embeddings.create(
        model=model_name,
        input=text,
        dimensions=512
    ).data[0].embedding


#tips:将合并成为text_content的字段的summary+comment做embedding
df['embedding']=df.text_content.apply(lambda x:text2vec(x,model_name="text-embedding-3-small"))


df.to_csv('./datas/output_embeddings.csv')
print('csv文件保存成功👌👌')

print(df.head(5))

