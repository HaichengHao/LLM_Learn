# @Time    : 2026/4/8 09:20
# @Author  : hero
# @File    : 01体验组件.py
import gradio as gr

def greet(name, intensity):
    return "Hello, " + name + "!" * intensity

demo = gr.Interface(
    fn=greet,
    inputs=["text", gr.Slider(value=2, minimum=1, maximum=10, step=1)],
    outputs=[gr.Textbox(label="greeting", lines=3)],
    api_name="predict"
)

demo.launch(
    inline=True,
    server_name='127.0.0.1',
    server_port=8080,
)