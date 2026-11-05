# @Time    : 2026/8/1 10:59
# @Author  : hero
# @File    : 00入门.py

from llama_index.core import VectorStoreIndex,SimpleDirectoryReader
documents=SimpleDirectoryReader(input_dir="./data").load_data() #tips:就像RAG学习中用的Loader
# documents=SimpleDirectoryReader(input_dir='./').load_data() #tips:就像RAG学习中用的Loader
index=VectorStoreIndex.from_documents(documents) #tips:返回的是一个索引类型
query_engine=index.as_query_engine() #tips:返回的是一个basequeryengine对象

response=query_engine.query("langchain是什么")

print(response)

'''
简要理解
1.调用SimpleDirectoryReader读取指定文件夹下的文件并加载为列表，可以按照之前RAG中的DocumentLoader的功能来理解
2.构建索引,把文件的索引构建出来
3.构建引擎，将索引加载为引擎

'''

