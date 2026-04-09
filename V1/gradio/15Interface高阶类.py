# @Time    : 2026/4/8 14:38
# @Author  : hero
# @File    : 15Interface高阶类.py

import gradio as gr

def greet(name):
    return f"Hello,{name}"
def greet2(name,age):
    return f"Hello,{name},你的年纪{age}"
main = gr.Interface(
    fn=greet,
    inputs="text", #tips:高层映射,将text映射为gr.Text(),

    outputs="text",
)

sub = gr.Interface(
    fn=greet2,
    inputs=["text","text"],  # tips:如果输入参数有两个的话

    outputs="text",
)

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )