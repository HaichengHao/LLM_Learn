# @Time    : 2026/5/16 09:07
# @Author  : hero
# @File    : service.py
import os
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, TextLoader, \
    CSVLoader, PyPDFLoader, UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'

embeddings=HuggingFaceEmbeddings(
    model_path=MODEL_PATH
)




class FileProcess:
    def __init__(self,ufile_pth):
        self.file_pth = ufile_pth
        self.file_suffix = os.path.splitext(ufile_pth)[1]

    def Docloader(self):
        return UnstructuredWordDocumentLoader(
            file_path=self.file_pth,
            mode='single'
        ).load()
    def CSVLoader(self):
        return CSVLoader(
            file_path=self.file_pth,
            mode='single'
        ).load()
    def PdfLoader(self):
        return PyPDFLoader(
            file_path=self.file_pth,
            mode='single'
        ).load()
    def TextLoader(self):
        return TextLoader(
            file_path=self.file_pth,
            encoding='utf-8',
        ).load()

    def docspliter(self,docs):
        return RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '。', '！', '？', '……', '，', ''],
            # tips:分割符列表,按顺序切分，现用句号切分，然后是感叹号，然后问号,然后省略号，然后逗号，然后空
            chunk_size=400,  # 每个块儿的最大长度
            chunk_overlap=50,  # tips:每个块重叠的长度,【重叠后向前取有效内容,且并不生成过小碎片】的核心分隔逻辑,不会让最后一个片段的有效内容只剩扣除重叠后的少量字符
            # important:需要小于chunk_size,建议为其10%-20%
            length_function=len,  # tips:可选,计算文本长度的函数，默认为字符串长度,可以自定义函数来实现token数切分
            add_start_index=True  # tips:可选,块的元数据中添加如此块起始索引
        ).split_documents(docs)
    def init_embeddings(self):
        return HuggingFaceEmbeddings(
            model_name=MODEL_PATH,
            model_kwargs={
                'device':'cuda:0' if torch.cuda.is_available() else 'cpu'
            }
        )

    def save2chroma(self,documents,embed_model,save_path):
        vectorstore=Chroma.from_documents(
            documents=documents,
            embed_model=embed_model,
            persist_directory=save_path
        )

        return vectorstore





