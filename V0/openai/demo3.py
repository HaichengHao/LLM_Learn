#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：LLM
@File    ：demo3.py
@IDE     ：PyCharm
@Author  ：百年
@Date    ：2026/3/20 16:57
'''
import numpy as np
import ast
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
base_url = os.getenv('base_url')
api_key = os.getenv('api_key')

client = OpenAI(base_url=base_url,api_key=api_key)
import pandas as pd

#step 3 被调用,将yummy beans转为向量
def text2vec(text,model_name):
    return client.embeddings.create(
        input=text,
        model=model_name,
        dimensions=512
    ).data[0].embedding

#tips:定义余弦相似计算
'''
余弦相似度是一个衡量两个非0向量之间夹角的度量,它给出的是这两个向量在多大程度上
指向相同的方向,余弦相似度的值域是[-1,1],其中1表示两个向量完全相同方向,-1表示完全相反方向,
而0则表示两个向量正交(即不相关)

consine_similarity=a dot b / ||a|| * ||b||  
分子是ab俩向量的点积,通过np.dot(a,b)来计算
分母是两个向量的L2范数(欧几里得长度),通过np.linalg.norm(a)和np.linalg.norm(b)来计算
'''


#step 4 被调用,进行输入向量和可以计算的embedding向量之间进行L2范数计算
#important: 定义计算两个向量之间L2范数的函数
def consine_distance_calc(a,b):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

#step 2调用search_text,传入df以及search_term="yummy beans",top_n=3
def search_text(df,search_term,top_n=3):
    #根据一个关键词(句),去搜索相似的评论,top_n指定搜索最相似的前三条评论

    #important:.literal_eval主要作用是解释和计算一个字符串
    #最终作用,把str变为矩阵❗⚠️
    #tips:因为csv是不支持直接存储复杂python对象的,所以其实demo2中进行embedding向量存储时候存入的是向量的字符串,而不是能计算的列表
    #  但是我们又想其可以转变为可以i计算的矩阵,所以就需要调用ast.literal_eval
    #   新开一个字段,这样就不影响原始数据
    df['embedding_vec'] = df['embedding'].apply(ast.literal_eval)

    #step 3 :
    #生成输入向量
    #tips:将yummy beans进行embedding,转换为512长度的向量
    input_vector = text2vec(search_term,model_name='text-embedding-3-small')

    #step 4:
    #tips:当我们自己的输入也转化为向量之后,就可以进行余弦相似计算了
    # important: 将输入向量与已经可以进行计算的embedding_vec向量字段列之间作余弦相似度计算
    df['similarity'] = df.embedding_vec.apply(lambda vec:consine_distance_calc(vec,input_vector))

    #tips:按相似度为排序依据让整个df做降序排序,并拿出前三个,并拿出它们的内容并将其转换为字符串对象,因为之前拼装过,所以我们把之前拼装时候用的字符串再替换掉方便我们查看
    results =  df.sort_values(by=['similarity'],ascending=False).head(top_n)['text_content'].str.replace('Summary:','').replace('; Text: ','')
    # 当然了,也可以不做处理 直接写 results=df.sort_values(by=['similarity'],ascending=False).head(top_n)

    for res in results:
        print(res)
        print('-'*30)






if __name__ == '__main__':
    #给一个关键词,去原始向量中搜索(demo2最后导出的csv中最后已经embedding的向量)相似的用户评论
    #读取原始数据
    df = pd.read_csv('./datas/output_embeddings.csv')

    #step : 1 将输入的yummy beans传入,只选取余弦距离最近的前三个

    search_text(df,search_term='yummy beans',top_n=3)

'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V0/openai/demo3.py 
yummy low fat snacks; Text: Pretty yummy for a low fat snack...crunchy and tasty with a little zing from the roasted peppers. You can also get them plain with sea salt which are also quite satisfying. Great substitute for chips and such which are just empty calories and impossible to eat only a few. I am pretty sure the lentil chips have some nutritional value as well..... and they don't taste like you are eating styrofoam like some of the rice cakes out there.
------------------------------
Good Buy; Text: I liked the beans. They were vacuum sealed, plump and moist. Would recommend them for any use. I personally split and stuck them in some vodka to make vanilla extract. Yum!
------------------------------
Plump, juicy vanilla beans; Text: These are plump, juicy vanilla beans! Perfect for ice cream making and making vanilla extract. Very satisfied and will not buy expensive vanilla beans at the grocery store ever again.
------------------------------
'''


