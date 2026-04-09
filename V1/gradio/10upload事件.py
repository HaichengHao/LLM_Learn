# @Time    : 2026/4/8 11:06
# @Author  : hero
# @File    : 10upload事件.py

import gradio as gr


def onupload(value):
    return value

with gr.Blocks() as main:
    files = gr.File(
        label='提交',
        # file_types=['jpg', 'png']
    )
    text = gr.Textbox(label="文件名")
    files.upload(
        fn=onupload,
        inputs=files,
        outputs=text,
    )

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )