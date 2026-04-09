# @Time    : 2026/4/8 19:57
# @Author  : hero
# @File    : 28gradio的部署.py


import gradio as gr
import pandas as pd

df = pd.DataFrame({"age":[20,22,18,10],"name":['niko','zzz','nox','ze'],"id":[101,102,103,104]})
df.set_index("id",inplace=True) #tips:让id作为列索引

with gr.Blocks() as demo:
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
    demo.launch(
        # server_name='localhost',
        # server_port=8888,
        share=True
    )


'''
想用debug模式的话主程序必须叫demo
启动的时候用gradio main.py即可

当launch中设置share为True的时候,此时可以将自己的gradio应用分配到公网,时效只有72小时

推荐在huggingface创建space并部署
'''