# @Time    : 2026/4/3 15:47
# @Author  : hero
# @File    : 17补充RecursiveDocumentspliter.py


'''
其实硬要说也不算是补充,因为还是一样的
'''

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')

embeddings=OpenAIEmbeddings(
    model='text-embedding-3-small',
    api_key=api_key,
    base_url=base_url,
)

loader = TextLoader(file_path='../assets/sample.txt')
documents = loader.load()


text_spliter=RecursiveCharacterTextSplitter(
    separators=['\n\n', '\n', '。', '！', '？', '……', '，', ''],  # tips:分割符列表,按顺序切分，现用句号切分，然后是感叹号，然后问号,然后省略号，然后逗号，然后空
    chunk_size=400,  # 每个块儿的最大长度
    chunk_overlap=50,  # tips:每个块重叠的长度,【重叠后向前取有效内容,且并不生成过小碎片】的核心分隔逻辑,不会让最后一个片段的有效内容只剩扣除重叠后的少量字符
    # important:需要小于chunk_size,建议为其10%-20%
    length_function=len,  # tips:可选,计算文本长度的函数，默认为字符串长度,可以自定义函数来实现token数切分
    add_start_index=True  # tips:可选,块的元数据中添加如此块起始索引

)

splitted_doc = text_spliter.split_documents(documents)
print(splitted_doc)

for splitted_doc_item in splitted_doc:
    print(f'文档片段{splitted_doc_item.page_content}')
    print(f'文档片段大小{len(splitted_doc_item.page_content)}')
    print(f'文档元数据{splitted_doc_item.metadata}')

# embed_doc=embeddings.embed_documents(splitted_doc)
# print(embed_doc)