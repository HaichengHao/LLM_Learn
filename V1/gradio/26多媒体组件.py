# @Time    : 2026/4/8 17:23
# @Author  : hero
# @File    : 26多媒体组件.py
import gradio as gr

with gr.Blocks() as main :
    gr.Image()
    gr.Video()
    gr.Audio()
    gr.File()
    gr.Markdown(
        """
        # 一级标题
        ## 二级标题
        ```python
        #python代码块 
        print('hello gradio')
        ```
        """
    )
    gr.HTML(
        """
        <h1>我是标题</h1>
        """
    )
if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8080,
    )