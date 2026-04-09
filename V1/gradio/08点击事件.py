# @Time    : 2026/4/8 10:33
# @Author  : hero
# @File    : 08点击事件.py

'''
类似于js当中的addEventListener('click', function() {xxx})
'''
import gradio as gr

with gr.Blocks() as main:
    #创建一个文本框接收用户的输入
    input_text=gr.Textbox(
        label='输入'
    )
    #创建按钮
    submitbtn=gr.Button(
        value='提交'
    )
    #创建一个文本框用于显示结果
    output_text=gr.Textbox(
        label='输出'
    )

    def on_click(value):
        return "您输入的是>>>"+value


    submitbtn.click(
        fn=on_click,
        inputs=input_text, #tips:函数fn(onclick)的参数
        outputs=output_text
    )

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
        favicon_path='./imgs/demoavatar.png' #tips:favicon
    )