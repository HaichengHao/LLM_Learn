# @Time    : 2026/3/29 17:26
# @Author  : hero
# @File    : main.py
from langchain_chroma import Chroma #important:导入需要的chroma
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'



#tips:定义切分器,传入加载器加载后的结构化doc,返回切分后的结果

def spliter(docs,chunk_size=400,chunk_overlap=50):
    return RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '。', '！', '？', '……', '，', ''],  # tips:分割符列表,按顺序切分，现用句号切分，然后是感叹号，然后问号,然后省略号，然后逗号，然后空
        chunk_size=chunk_size,  # 每个块儿的最大长度
        chunk_overlap=chunk_overlap,  # tips:每个块重叠的长度
        length_function=len,  # tips:可选,计算文本长度的函数，默认为字符串长度,可以自定义函数来实现token数切分
        add_start_index=True  # tips:可选,块的元数据中添加如此块起始索引
    ).split_documents(docs)

#tips:定义文档加载器,返回结构化后的文档结果
def docloader(doc_path):
    return UnstructuredWordDocumentLoader(file_path=doc_path,mode='single').load()

#tips：定义Embedding功能,返回构建的嵌入模型

def embed_model(model_path=MODEL_PATH):
    return HuggingFaceEmbeddings(
    model_name=model_path,
    model_kwargs={
        'device':'cuda:0' if torch.cuda.is_available() else 'cpu'
    }
)

#tips:定义存入chromaDB

def save2chroma(documents,embed_model,save_path):
    vectorstore = Chroma.from_documents(
        documents=documents, #tips:接受一个文档切分后的列表
        embedding=embed_model, #tips 传入一个embedding模型
        persist_directory=save_path #tips:传入db文件要保存的路径
    )

    #tips:还有另外一种写法噢!⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️⚠️️️
    vectorstore2 = Chroma(
        collection_name='example_collection',
        embedding_function=embed_model,
        persist_directory=save_path
    )
    print(f'向量库已经保存至{save_path}🎉')
    return vectorstore

if __name__ == '__main__':
    doc_pth = '../../assets/sample.docx'
    docs = docloader(doc_pth) #tips:先将其转换为结构化数据
    splited_res = spliter(docs,chunk_size=400,chunk_overlap=50) #tips:然后再进行分词
    target_embed_model=embed_model() #tips:实例化embedding模型
    vector_db = save2chroma( #tips:存入chroma
        documents=splited_res,
        embed_model=target_embed_model,
        save_path='./chroma_db'

    )

"""
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/RAG/case/00将embedding后的数据存入chroma/main.py 
Loading weights: 100%|██████████| 391/391 [00:00<00:00, 54415.45it/s]
BertModel LOAD REPORT from: /home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116
Key                     | Status     |  | 
------------------------+------------+--+-
embeddings.position_ids | UNEXPECTED |  | 

Notes:
- UNEXPECTED	:can be ignored when loading from different task/architecture; not ok if you expect identical arch.
向量库已经保存至./chroma_db🎉
"""


'''
总结
使用非结构化docx文档加载器调用.load()之后返回的是一个结构化的文档列表,而且默认指定的是single模式,所以只会有一个元素,
但是这样还是不够精细的,所以用切分器将其切分,然后得到的是切分后的列表,这样之后元素可就多了,这个列表变得不再单一,而是切分出了多块儿元素  
之后还需要定义一个返回模型的函数并最终构建存入chroma的函数,传入分割后的结构化文档列表,然后传入embedding模型,并传入db路径
这之后将会把文档embedding后的数据存入指定路径下并生成db文件(sqlite)


'''