# @Time    : 2026/4/8 11:37
# @Author  : hero
# @File    : 11练习1.py

import gradio as gr
with gr.Blocks() as main:
    def greet(uname,uage):
        return f"Hello {uname},你的年龄是{uage}"
    with gr.Row():

        uname = gr.Textbox(placeholder='输入姓名')
        uage = gr.Slider(minimum=18,maximum=100,step=1,label='输入年龄',interactive=True)

    output = gr.Textbox(label='输出结果')
    btn = gr.Button(value="提交")

    btn.click(
        fn=greet,
        inputs=[uname, uage],
        outputs=output
    )
if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )
