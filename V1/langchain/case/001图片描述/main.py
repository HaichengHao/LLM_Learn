# @Time    : 2026/3/27 14:23
# @Author  : hero
# @File    : main.py
from fastapi import FastAPI, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

from pydantic import BaseModel
from fastapi.responses import StreamingResponse #tips:流式响应需要用
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
load_dotenv()

app = FastAPI(
    title='多模态图片描述',
    version='0.0.1'
)
origins=[
    'http://localhost',
    'http://localhost:3000',
    'http://127.0.0.1:5500',
    'http://127.0.0.1:8080',
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key=os.getenv('api_key')
base_url = os.getenv('base_url')
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

model1 = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini',
    # streaming=True
)
model2 = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini',
    streaming=True
)

prompt_template = ChatPromptTemplate(
    messages=[
        ('system','用中文描述图片内容'),
        ('human',[
            {'type':'text','text':'请描述这张图片:'},
            {'type':'image_url','image_url':'{image_url}'}
        ])
    ]
)

parser = StrOutputParser()
chain = prompt_template|model1|parser

#tips:定义请求体模型
class ImageRequest(BaseModel):
    image_url: str

#tips:响应模板
class Description(BaseModel):
    description: str

@app.post('/describeimg',response_model=Description)
async def describe_img(request:ImageRequest):
    try:
        result = await chain.ainvoke({'image_url':request.image_url})
        return {'description':result}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'处理图片时出错{str(e)}')


#important:再来个流式

chain2 = prompt_template|model2

@app.post('/describe/stream')
async def describe_stream(request:ImageRequest):
    """
    流式返回图片描述,每个chunk是一个token,
    响应类型:text/plain;charset=utf-8
    :param request:
    :return:
    """
    async def event_generator():
        try:
            async for chunk in chain2.astream({'image_url':request.image_url}):
                content=chunk.content
                if content:
                    yield content
        except Exception as e:
            error_msg = f'流式输出出错{str(e)}'
            print(error_msg)
            yield error_msg
            return

    #important:构造流式响应,可以传入我们的生成器对象生成的内容,这样生成和响应就都是流式响应了
    return StreamingResponse(event_generator(),media_type='text/plain; charset=utf-8')

    '''
    class StreamingResponse(Response):
    body_iterator: AsyncContentStream

    def __init__(
        self,
        content: ContentStream,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
    
    '''
#     tips:可以看一下源码,上面要求传入的是一个可迭代的同步或者异步对象，我定义的event_generator就是异步生成器,生成异步content

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)