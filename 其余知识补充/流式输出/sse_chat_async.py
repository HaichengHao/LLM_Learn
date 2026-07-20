# @Time    : 2026/6/29
# @Author  : hero (Async SSE version)
# @File    : sse_chat_async.py
from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import uvicorn
import os
import json
import asyncio

load_dotenv()

llm = init_chat_model(
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
        ('system', '你现在是一位小说家'),
        ('human', '{user_input}')
    ]
)

chain = chat_prompt_template | llm | StrOutputParser()


async def generate_sse_stream_async(user_input: str):
    """异步生成 SSE 流"""
    try:
        # 使用 astream 异步流
        async for chunk in chain.astream({"user_input": user_input}):
            if chunk:
                # 发送 data: ... 格式
                yield f"data: {json.dumps(chunk)}\n\n"
                # 可选：加一点延迟避免太快（一般不需要）
                # await asyncio.sleep(0.01)
        yield "data: [DONE]\n\n"
    except Exception as e:
        error_msg = {"error": str(e)}
        yield f"data: {json.dumps(error_msg)}\n\n"


@app.get("/chat/sse")
async def sse_chat(request: Request, user_input: str = Query(...)):
    """
    SSE 接口，支持异步流式响应
    注意：FastAPI 自动处理 AsyncGenerator
    """
    return StreamingResponse(
        generate_sse_stream_async(user_input),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        }
    )


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
