# @Time    : 2026/4/8 14:56
# @Author  : hero
# @File    : 16常见组件.py
import gradio as gr
fruit_lst=["西瓜","苹果","菠萝"]
def demofn(a,b,c,d,e):
    return f"{a},{b},{c},{d},{e}"
demo = gr.Interface(
    fn=demofn,
    inputs=[
        gr.Slider(minimum=2,maximum=10,step=2,label='计数器',info="choose between 2 and 10"),
        gr.Dropdown(choices=fruit_lst,interactive=True,info="choose your favorite fruit",label="水果选择器",value=fruit_lst[0]), #value控制默认选中的是哪个
        gr.CheckboxGroup(['a','b','c'],label='多选'),
        gr.Radio(['s','m','l','xl'],label='单选'),
        gr.Checkbox(label="我同意") #tips:勾选

    ],
    outputs="text",
    examples=[
        [2,'苹果',['a','b'],'m',True],
        [12,'菠萝',['a','b','c'],'l',False],
        [20,'西瓜',['a','b','c'],'m',True],
    ],
    title="这是一个示例",
    description="这是描述信息",
    article="这个出现在最下方,可以写引文"

)

if __name__ == '__main__':

    demo.launch(
        server_name='localhost',
        server_port=8080,
    )