# @Time    : 2026/4/8 17:28
# @Author  : hero
# @File    : 27数据图组件.py

import gradio as gr
import pandas as pd

df = pd.DataFrame({"age":[20,22,18,10],"name":['niko','zzz','nox','ze'],"id":[101,102,103,104]})
df.set_index("id",inplace=True) #tips:让id作为列索引

with gr.Blocks() as main:
    gr.LinePlot(
        df,
        x="name",
        y="age",

    )
    gr.ScatterPlot(
        df,
        x="name",
        y="age",
    )
    gr.BarPlot(
        df,
        x="name",
        y="age",
    )


if __name__ == '__main__':
    main.launch(
        server_name='localhost',
        server_port=8888,
    )