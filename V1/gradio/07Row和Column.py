# @Time    : 2026/4/8 10:25
# @Author  : hero
# @File    : 07Row和Column.py

'''
gr.Row 创建一行,并在其中可以安排多个组件
gr.Column(scale) 用于设置列表在行中的比例
'''

import gradio as gr

with gr.Blocks() as main:
    with gr.Row():
        #左边的列，占4成比例
        with gr.Column(scale=4):
            gr.Textbox(label='左边的输入框')

        #右边的列，占1成
        with gr.Column(scale=1):
            gr.Slider(minimum=0, maximum=100, step=10)

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8888,
    )