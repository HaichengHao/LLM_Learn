# @Time    : 2026/6/6 11:44
# @Author  : hero
# @File    : websocket_resp.py
from fastapi import FastAPI,WebSocket
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import uvicorn
import os

from starlette.websockets import WebSocketDisconnect

load_dotenv()

llm=init_chat_model(
    model='glm-4.7',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

chat_prompt_template = ChatPromptTemplate(
    messages=[
        ('system','你现在是一位小说家'),
        ('human','{user_input}')
    ]
)

chain = chat_prompt_template|llm|StrOutputParser()

# 定义请求体模型（用于验证）
class ChatRequest(BaseModel):
    user_input: str


@app.websocket('/chat/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() #important:建立握手请求
    try:
        while True:
            #接受客户端消息
            data = await websocket.receive_text() #tips:异步等待客户端发送文本消息

            #解析json
            try:
                request=ChatRequest.model_validate_json(data) #tips:验证传入的data是否符合定义的Pydantic请求模型ChatRequest
            except Exception as e:
                await websocket.send_text(f'[ERROR] Invalid JSON {str(e)}')
                continue

            async for chunk in chain.astream({
                'user_input': request.user_input
            }):
                if chunk:
                    await websocket.send_text(chunk)

            #发送结束标记
            await websocket.send_text('[DONE]')

    except WebSocketDisconnect:
        print('Client disconnected')

    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_text(f"[ERROR] {str(e)}")

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)