# @Time    : 2026/4/8 11:52
# @Author  : hero
# @File    : 12练习2.py
import gradio as gr
#tips:定义一个水果的列表
fruits_lst=["🍌香蕉","🍎苹果","🍍菠萝"]

def display_choiced(selected_fruit):
    return f"您选择的水果是>>{selected_fruit}"

with gr.Blocks() as main:
    #添加一个标题=>HTML标签
    gr.HTML("<h1 align='center'>请选择您的水果</h1>")
    #创建一个行布局
    with gr.Row():
        #创建一个下拉框让用户选择
        fruits = gr.Dropdown(
            label="请选择一种水果",
            choices=fruits_lst,
            interactive=True,
            value=fruits_lst[0] #tips:默认值,也就是前端中options的selected状态
        )

    #创建一个文本框，用于用户选择水果的显示
    output = gr.Textbox(
        label="你选择的水果"
    )

    #tips:给下拉框添加事件,添加change事件,选择之后直接输出选择的水果
    fruits.change(
        fn=display_choiced,
        inputs=fruits,
        outputs=output
    )



if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
        debug=True
    )