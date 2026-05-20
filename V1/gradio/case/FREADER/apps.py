# @Time    : 2026/5/16 09:07
# @Author  : hero
# @File    : apps.py
import os
import json
import datetime
from pathlib import Path
from redis.asyncio import Redis
import uvicorn
from fastapi import FastAPI, UploadFile,Query,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import uuid as uuidlib

#初始化Redis连接
REDIS_URL = "redis://127.0.0.1:6379/0"
redis_client = Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)
uploaddir = './assets'  # tips:创建上传文件夹

os.makedirs(uploaddir, exist_ok=True)
file_suffix_allowed=['.csv','.docx','.pdf','.md','.txt']
app = FastAPI(
    description="文件上传接口"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/upload/')
async def upload_file(file: UploadFile):#tips:它是要比File方式更好的，因为它不用指定bytes类型，而且这样它就是一个在flask中学过的filestorge类型
    if not file.filename:
        raise HTTPException(status_code=400,detail="文件为空,上传失败")


    full_file_name=file.filename
    file_name=Path(full_file_name).name
    file_suffix=Path(full_file_name).suffix

    if file_suffix in file_suffix_allowed:
        origin_name = full_file_name
        safe_filename = f"{uuidlib.uuid4().hex}{file_suffix}"
        safe_path=os.path.join(uploaddir,safe_filename)
        async with aiofiles.open(safe_path,mode='wb') as f:
            while chunk := await file.read(1024*1024):await f.write(chunk)
        meta={
            'origin_name':origin_name,
            'saved_path':safe_path,
            'size':os.path.getsize(safe_path),
            'uploaded_at':''
        }
        return {
            'msg':'文件上传成功',
            'origin_name':origin_name,
            'info':'file_upload_success',
            'filepath':safe_path
        }
    else:
        return {
            'msg':'文件上传失败,格式有问题',
            'info':'file_upload_fail'
        }


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=58888)