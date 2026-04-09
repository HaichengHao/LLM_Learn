# @Time    : 2026/4/8 09:39
# @Author  : hero
# @File    : 03Slider.py

import gradio as gr

with gr.Blocks() as demo:
    gr.Slider(
        minimum=0,
        maximum=22,
        step=1,
        label='选择进度'
    )
if __name__ == '__main__':

    demo.launch(
        server_name='localhost',
        server_port=8080,
    )