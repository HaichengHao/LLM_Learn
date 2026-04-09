# @Time    : 2026/4/8 09:29
# @Author  : hero
# @File    : 01Textbox.py

import gradio as gr

with gr.Blocks() as demo:
    gr.Textbox(
        label='标题',
        placeholder='占位'
    )

if __name__ == '__main__':
    demo.launch(
        server_name='localhost',
        server_port=8080,
    )