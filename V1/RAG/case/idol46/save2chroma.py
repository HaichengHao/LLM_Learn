# @Time    : 2026/4/11 11:06
# @Author  : hero
# @File    : save2chroma.py
from langchain_chroma import Chroma
from  langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter,JSFrameworkTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import torch
MODEL_PATH ='/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'

'''
四步
1.doc=loader(doc_path).load()
2.splited_doc=docspliter.split(doc)   json结构清晰，不需要了
3.构建embeddings模型
4.构建save2chroma
'''



def  loaded_doc(doc_path:str):
    """
       加载JSON文件，并为 members 和 singles 分别创建文档。
    """
    docs=[]

    # 1. 加载所有成员，每个成员作为一个Document(),这里遗忘的话就看code里面的03
    members_doc=JSONLoader(
        file_path=doc_path,
        jq_schema='.members[]', # 提取 members 数组中的每个对象
        text_content=False   #保持为JSON对象,而不是转成字符串
    ).load()

    docs.extend(members_doc)

    # 2. 加载所有单曲，每首单曲作为一个Document
    singles_docs = JSONLoader(
        file_path=doc_path,
        jq_schema='.singles[]',  # 提取 singles 数组中的每个对象
        text_content=False
    ).load()
    docs.extend(singles_docs)


    return docs #tips:还是列表里面包含Document对象,就像这样[Document(...),Document(...),...]
#
#
# def splited_doc(doc,chunk_size=400,chunk_overlap=50):
#     return RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,  # 每个块儿的最大长度
#         chunk_overlap=chunk_overlap,  # tips:每个块重叠的长度
#         length_function=len,  # tips:可选,计算文本长度的函数，默认为字符串长度,可以自定义函数来实现token数切分
#         add_start_index=True  # tips:可选,块的元数据中添加如此块起始索引
#     ).split_documents(doc)


def  embedding_model(UMODEL_PATH:str=MODEL_PATH):
    return HuggingFaceEmbeddings(
        model_name=UMODEL_PATH,
        model_kwargs={
            'device':'cuda:0' if  torch.cuda.is_available() else 'cpu'
        }
    )


def save2chroma(udoc,save_path:str,embedding_model):
    return Chroma.from_documents(
        documents=udoc,
        embedding=embedding_model,
        persist_directory=save_path,

    )


def main():
    docpath = './idol46.json'
    udoc = loaded_doc(docpath) # 现在 udoc 是一个包含所有成员和单曲的文档列表
    print(f'成功加载{len(udoc)}个文档(成员+单曲)')
    #实例化模型
    umodel=embedding_model()
    save2chroma(
        udoc,
        save_path='./idol46_chroma',
        embedding_model=umodel
    )


if __name__ == '__main__':
    main()
    print('数据成功存入数据库')