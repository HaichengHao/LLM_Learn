# @Time    : 2026/6/6 10:11
# @Author  : hero
# @File    : http_or_https_stream_resp.py

import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI,Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

load_dotenv()

#定义程序
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#初始化大模型
llm=init_chat_model(
    model='glm-4.7',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)



#定义提示词
prompt_template = ChatPromptTemplate(
    messages=[
        ('system','你现在是一个小说家，你会讲小说'),
        ('human','{user_input}')
    ]
)


#定义lcel

chain=prompt_template|llm|StrOutputParser()


#定义接口
@app.post('/chat/stream_resp',response_class=StreamingResponse)

async def chat_stream_resp(user_input:str=Body(...,embed=True)):
    #important:需要注意的是当函数参数没有使用 Body(), Query(), Path() 等显式声明时，它会尝试从 JSON 请求体的根级别 解析该字段
    # embed=True 告诉 FastAPI：这个参数应该在一个 JSON 对象里，键名就是参数名

    async def event_generator():
        async for chunk in chain.astream(
                {'user_input': user_input},

        ):
            if chunk:
                yield chunk.encode('utf-8')  #tips:生成chunk,是异步可迭代的

    return StreamingResponse(  #tips:要求传入一个异步可迭代对象
        event_generator(),media_type='text/plain' )



#important:方案2,构建自定义请求体，更规范
class ChatRequest(BaseModel):
    user_input: str

@app.post('/chat/stream_resp')
async def chat_stream_resp(request: ChatRequest):
    async def event_generator():
        async for chunk in chain.astream({'user_input': request.user_input}):
            if chunk:
                yield chunk.encode('utf-8')
    return StreamingResponse(event_generator(), media_type='text/plain')

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)