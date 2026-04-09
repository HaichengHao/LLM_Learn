# @Time    : 2026/4/8 10:17
# @Author  : hero
# @File    : 06Chatbot.py

import gradio as gr

with gr.Blocks() as main:
    gr.Chatbot(
        label='小海豹',
        avatar_images=[
            './imgs/demoavatar.png',
            './imgs/demoavatar2.png',
        ]
    )

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8888,
    )