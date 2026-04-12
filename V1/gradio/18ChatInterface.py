# @Time    : 2026/4/8 15:57
# @Author  : hero
# @File    : 18ChatInterface.py

import gradio as gr


def echo(msg,history): #但是要求传入message和history
    print(history)
    return f'your typed:{msg}'

demo = gr.ChatInterface( #不用传入输入输出和调用的函数
    fn=echo,
    autofocus=True, #tips:实现每次对话完毕之后光标默认回到对话框内
    title="对话机器人框架原型",
    examples=['什么是Gradio','Langchain于llmindex的区别'],
    submit_btn='发送'



)

if __name__ == '__main__':
    demo.launch(
        server_name='localhost',
        server_port=8080,
    )