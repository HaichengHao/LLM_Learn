# @Time    : 2026/4/8 15:27
# @Author  : hero
# @File    : 17TabbedInterface类.py

'''
可以在一个页面上写多个tab栏目切换
'''

import gradio as gr
def sayhi(name):
    return f"Hi {name}"

def saybye(name):
    return f"Bye,{name}"

sub1 = gr.Interface(
    sayhi,
    inputs="text",
    outputs="text",
)

sub2 = gr.Interface(
    saybye,
    inputs="text",
    outputs="text",
)


main = gr.TabbedInterface(
    interface_list=[sub1, sub2],
    tab_names=['hi','bye']

)


if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )