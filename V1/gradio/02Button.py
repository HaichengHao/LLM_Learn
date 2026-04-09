# @Time    : 2026/4/8 09:37
# @Author  : hero
# @File    : 02Button.py

import gradio as gr
with gr.Blocks() as demo:
    gr.Button(value='点我提交',size='small')

if __name__ == '__main__':
    demo.launch(
        server_name='localhost',
        server_port=8080,
    )