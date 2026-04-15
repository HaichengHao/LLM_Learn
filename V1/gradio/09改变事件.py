# @Time    : 2026/4/8 10:54
# @Author  : hero
# @File    : 09改变事件.py
'''
相当于js中的addEventListener('change', function() {xxxxx}
比如说滑块滑动的时候，滑块上的数字发生改变了，那么就会触发改变事件



'''


import gradio as gr

def get_slide_value(v):
    return f"您选择的值是{v}"
with gr.Blocks() as main:
    #创建一个滑块组件
    slide = gr.Slider(minimum=0,maximum=100,value=50,label='调节',interactive=True)#important:interactive=True的时候,那么这个滑块可以和用户进行交互
    #创建一个文本组件，用于显示结果
    output_txt = gr.Textbox(
        label='结果'
    )
    slide.change(
        get_slide_value,
        inputs=slide,
        outputs=output_txt

    )

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080
    )