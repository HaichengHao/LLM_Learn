#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：LLM 
@File    ：demo1.py
@IDE     ：PyCharm 
@Author  ：百年
@Date    ：2026/3/20 15:18 
'''


from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('api_key')
client = OpenAI(
    base_url='https://xiaoai.plus/v1',
    api_key=api_key
)

#tips:发送请求,调用openai的embeddings接口
resp = client.embeddings.create(
    model='text-embedding-3-small',
    input='aloha',
    dimensions=512 #tips:指定维度
)

print(resp.data[0].embedding)
print(len(resp.data[0]))

"""
Embeddings(嵌入)在自然语言处理(NLP)中起着至关重要的作用,它们的主要目的是将高维,
离散的文本数据(如单词或短语)转换为低维、连续的向量表示,这些向量不仅编码了词本身的的含义 
还捕捉到了词语之间的寓意和句法关系,通过embeddings,原本难以直接处理的文本数据可以被机器学习模型
理解和操作

它就是将[不可计算][非结构化]的词转换为[可计算][结构化]的向量
"""