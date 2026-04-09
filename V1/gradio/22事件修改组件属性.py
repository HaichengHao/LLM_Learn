# @Time    : 2026/4/8 16:51
# @Author  : hero
# @File    : 22事件修改组件属性.py

import gradio as gr
def modiFY(v):
    return gr.Number(visible=v)

with gr.Blocks() as main:
    inp= gr.Checkbox()
    outp=gr.Textbox()

    inp.change(
        modiFY,
        inputs=inp,
        outputs=outp,
    )

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )