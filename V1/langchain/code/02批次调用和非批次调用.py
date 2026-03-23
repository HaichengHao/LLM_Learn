from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv('api_key')
openai_base_url = os.getenv('base_url')

openaillm = ChatOpenAI(
    model='gpt-4o-mini',
    api_key=openai_api_key,
    base_url=openai_base_url,
    temperature=1.0
)

# 定义一个通用模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个诗人"),
    ("user", "{instruction}")
])

parser = StrOutputParser()
chain = prompt | openaillm | parser

# 准备多个不同的指令
inputs = [
    {"instruction": "写一首七言诗赞美春天"},
    {"instruction": "写一首五言诗赞美夏天"},
    {"instruction": "写一首七言诗赞美冬天"},
]

# 批量调用
results = chain.batch(inputs)

for i, res in enumerate(results, 1):
    print(f"=== 诗 {i} ===")
    print(res)
    print()