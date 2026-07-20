# @Time    : 2026/6/29
# @Author  : hero (modified for SSE)
# @File    : sse_chat.py
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import uvicorn
import os
import json

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


def generate_sse_stream(user_input: str):
    """生成符合 SSE 格式的流"""
    try:
        for chunk in chain.stream({"user_input": user_input}):
            if chunk:
                # SSE 要求 data 行以 "data: " 开头，结尾双换行
                yield f"data: {json.dumps(chunk)}\n\n"
        # 发送结束信号（可选）
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.get("/chat/sse")
async def sse_chat(user_input: str = Query(..., description="用户输入")):
    return StreamingResponse(
        generate_sse_stream(user_input),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        }
    )


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
