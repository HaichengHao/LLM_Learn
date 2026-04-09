# @Time    : 2026/4/8 10:12
# @Author  : hero
# @File    : 05File.py

import gradio as gr

with gr.Blocks() as main:
    gr.File(
      file_types= ['png','jpg','jpeg'], #tips:允许上传的文件类型
    )

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )
