# @Time    : 2026/4/8 16:06
# @Author  : hero
# @File    : 19回到Blocks.py
import gradio as gr
def say_hello(i):
    return f'Hello {i}!'
with gr.Blocks() as main:
    input= gr.Textbox()
    output=gr.Textbox()
    btn=gr.Button(value="点我提交或者回车提交")
    input.submit(
        fn=say_hello,
        inputs=input,
        outputs=output,
    )
    btn.click(
        fn=say_hello,
        inputs=input,
        outputs=output,
    )