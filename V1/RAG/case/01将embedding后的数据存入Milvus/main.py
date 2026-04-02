# @Time    : 2026/4/2 13:28
# @Author  : hero
# @File    : main.py


'''
流程
1.读取数据,需要loader.load()
2.进行分词，需要splitor.split(doc)
3.构建像量化模型
4.构建milvus进行存入

uv add pymilvus milvus-lite langchain-milvus pymilvus[milvus_lite]
'''
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from dotenv import load_dotenv
import os
load_dotenv()
zai_key =os.getenv('zhipu_key')
zai_base_url =os.getenv('zhipu_base_url')
langsmith_key =os.getenv('lang_smith_key')
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = f'{langsmith_key}'


#step 实现load功能

def load_doc(doc_path):
    return UnstructuredWordDocumentLoader(file_path=doc_path,mode='single').load()

#step 实现分词功能

def split_doc(doc,chunk_size=400,chunk_overlap=50):
    return RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '。', '！', '？', '……', '，', ''],  # tips:分割符列表,按顺序切分，现用句号切分，然后是感叹号，然后问号,然后省略号，然后逗号，然后空
        chunk_size=chunk_size,  # 每个块儿的最大长度
        chunk_overlap=chunk_overlap,  # tips:每个块重叠的长度
        length_function=len,  # tips:可选,计算文本长度的函数，默认为字符串长度,可以自定义函数来实现token数切分
        add_start_index=True  # tips:可选,块的元数据中添加如此块起始索引
    ).split_documents(doc)

#step 定义像量化模型
def embedmodel():
    return OpenAIEmbeddings(
        model='embedding-3',
        api_key=zai_key,
        base_url=zai_base_url,
        # dimensions=128, #tips:有的大模型不支持自定义embedding维度
        chunk_size=32 #important:智谱有限制,chunk为64,这里我给到32
    )

#step 定义Milvus

#tips:这里有两种方式,一种是使用socket,还有一种是基于sqlite的本地方式

local_db='./milvus_demo.db'
socket_db='http://127.0.0.1:19530' #tips:注意我是用docker的,映射的端口是19530
'''
如果用的是docker的话,
nikofox@MOSS:~/Milvus$ wget https://github.com/milvus-io/milvus/releases/download/v2.4.6/milvus-standalone-docker-compose.yml
nikofox@MOSS:~/Milvus$ docker compose -f milvus-standalone-docker-compose.yml up -d
docker compose -f  milvus-standalone-docker-compose.yml down 如果要停掉的话就这样写
'''


# def vec2milvus(doc_vec, embed_model, collection_name="vec_docs", db_href="http://127.0.0.1:19530"):
#     vector_db = Milvus(
#         embedding_function=embed_model,
#         collection_name=collection_name,
#         connection_args={
#             "uri": db_href
#         },
#         drop_old=True,
#         auto_id=True
#     )
#
#     vector_db.add_documents(doc_vec)
#
#     return vector_db

from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

def vec2milvus(doc_vec, embed_model, collection_name="vec_docs"):

    # 1. 连接
    connections.connect("default", uri="http://127.0.0.1:19530")

    # 2. 文本 + embedding
    texts = [doc.page_content for doc in doc_vec]
    embeddings = embed_model.embed_documents(texts)
    dim = len(embeddings[0])

    print(f"向量维度: {dim}")

    # 3. 清空旧集合（开发阶段）
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)

    # 4. schema
    fields = [
        FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema("vector", DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema("text", DataType.VARCHAR, max_length=2000),
    ]
    schema = CollectionSchema(fields)

    # 5. 创建集合
    collection = Collection(collection_name, schema)

    # 6. 建索引（关键！）
    collection.create_index(
        field_name="vector",
        index_params={
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
    )

    # 7. 插入数据
    collection.insert([embeddings, texts])

    # 8. 加载
    collection.load()

    print("✅ 写入完成")

    return collection
def search(query, embed_model, collection_name="vec_docs"):
    from pymilvus import Collection

    collection = Collection(collection_name)

    query_vec = embed_model.embed_query(query)

    results = collection.search(
        data=[query_vec],
        anns_field="vector",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=3,
        output_fields=["text"]
    )

    for hits in results:
        for hit in hits:
            print("👉 相似内容：", hit.entity.get("text"))
if __name__ == '__main__':
    demodoc = load_doc('../../assets/sample.docx')
    split_res = split_doc(demodoc)
    target_embed_model = embedmodel()
    vec2milvus(
        doc_vec=split_res,
        embed_model=target_embed_model,
        db_href='http://127.0.0.1:19530'
    )
    print('成功!!!')
    print("\n=== 测试查询 ===\n")
    search("这篇文档讲了什么？", target_embed_model)