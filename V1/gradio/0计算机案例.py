# @Time    : 2026/3/26 17:47
# @Author  : hero
# @File    : 0计算机案例.py
import gradio as gr

def calculator(num1,operation,num2):
    if operation == '+':
        return num1+num2
    elif operation == '-':
        return num1-num2
    elif operation == '✖':
        return num1*num2
    elif operation == '➗':
        if num2 == 0:
            raise gr.Error('除数不能为0⚠️')
        return num1/num2
    return 0

instence = gr.Interface(
    fn=calculator,
    inputs=[
        'number',
        gr.Radio(choices=['+','-','✖','➗'],label='运算符号'),
        'number'
    ],
    outputs='number'
)


#tips:启动就用instence.launch
instence.launch(
    inline=True,
    server_name='127.0.0.1',
    server_port=8088,
    auth=('admin','123456'),
    # theme='light'

)