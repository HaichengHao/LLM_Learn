# @Time    : 2026/4/8 09:46
# @Author  : hero
# @File    : 04DropDown.py
'''
类似于前端中的select options那种
'''
import gradio as gr

with gr.Blocks() as demo:
    dropdown = gr.Dropdown(
        choices=[
            '北京',
            '上海',
            '深圳',
            '广州',
            '南京',
            '郑州'
        ],
        label="城市",
        allow_custom_value=True,
        interactive=True #important：允许交互,不然下拉框拉不动的
    )

if __name__ == '__main__':
    demo.launch(
        server_name='localhost',
        server_port=8080,
    )
