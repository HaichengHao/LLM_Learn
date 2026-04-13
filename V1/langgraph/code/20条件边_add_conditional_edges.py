# @Time    : 2026/4/13 15:47
# @Author  : hero
# @File    : 20条件边_add_conditional_edges.py
'''
如果想`选择性`地路由到一个或多个边(或选择性地终止),可以使用
`graph.add_conditiional(node_name,routing_function)`

与节点类似，routing_function接受图的当前状态(state)并返回一个值
默认情况下,routing_function 的返回值用作下一个要发送状态的节点（或节点列表）的名称。所有这些节点都将在下一个超级步骤中并行运行。
你可以选择提供一个字典，将 routing_function 的输出映射到下一个节点的名称。
graph.add_conditional_edges("node_a", routing_function, {True: "node_b", False: "node_c"})
'''