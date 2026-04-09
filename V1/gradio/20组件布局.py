# @Time    : 2026/4/8 16:10
# @Author  : hero
# @File    : 20组件布局.py

import gradio as gr

'''
布局组件简介

gr.Row:将组件水平排列
gr.Column:将组件竖直排列
gr.Group:用于对一组组件进行逻辑分组,通常在不显式控制布局时使用
gr.Tab:创建选项卡布局,用于在页面中分隔不同内容
gr.Accordion 创建可折叠的内容块
'''

with gr.Blocks() as main:
    with gr.Accordion("version_0.1",open=False): #tips:open控制是否展开
        with gr.Tab("demo1"):
            with gr.Row():
                gr.Text("Hello World")
                with gr.Column():
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