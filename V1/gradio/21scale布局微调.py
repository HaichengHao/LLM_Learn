# @Time    : 2026/4/8 16:21
# @Author  : hero
# @File    : 21scale布局微调.py

import gradio as gr


with gr.Blocks() as main:
    with gr.Accordion("version_0.1",open=False): #tips:open控制是否展开
        with gr.Tab("demo1"):
            with gr.Row():
                gr.Text("Hello World",scale=3)
                with gr.Column(scale=2):
                    gr.Text("Hello World")
                    gr.Text("Hello World")
        with gr.Tab("demo2"):
            with gr.Row():
                gr.Text("Hello NIKOFOX")
                with gr.Column():
                    gr.Text("Hello nikofox")
                    gr.Text("Hello nikofox")


if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )