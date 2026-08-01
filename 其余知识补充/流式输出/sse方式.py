# @Time    : 2026/7/14 10:41
# @Author  : hero
# @File    : sse方式.py
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse,ServerSentEvent
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
app=FastAPI()

load_dotenv()

LLM=init_chat_model(
    model='glm-4.7',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)


class ChatRequest(BaseModel):
    message: str


@app.post('/api/chat/stream',response_model=ChatRequest)
async def chat_stream(req:ChatRequest):
    async for ev in LLM.astream(req.message):
        if ev.get('type')=='_done': #自定义结束消息
            return
        yield ServerSentEvent(data=ev)

if __name__ == '__main__':
    #启动服务
    uvicorn.run(app, host='0.0.0.0', port=8000)