# @Time    : 2026/4/8 17:10
# @Author  : hero
# @File    : 24对话状态.py

import gradio as gr
def add_book(book,books:list[str]):
    books.append(book)
    return books
with gr.Blocks() as main :
    books=gr.State([])
    inp=gr.Textbox()
    outp=gr.Textbox()
    btn=gr.Button('添加图书')
    btn.click(
        add_book,
        inputs=[inp,books],
        outputs=outp
    )

if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8888,
    )