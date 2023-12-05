import streamlit as st
from streamlit_echarts import st_pyecharts
from pyecharts import options as opts
from pyecharts.charts import HeatMap
import pandas as pd
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Graph
from pyecharts.charts import Bar
import numpy as np


st.set_page_config(layout="wide", page_icon=None,
                   initial_sidebar_state="collapsed", page_title=None)

hide_st_style = """
            <style>
            /* Removes padding, margin and set full height to the main content area */
            .main .block-container { 
                padding-top: 0rem; 
                padding-right: 0rem;
                padding-left: 1rem;
                padding-bottom: 0rem;
                margin: 0;
            }
            /* Additional custom styles can be added here */
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 页面比例
page_ratio = st.slider('Page Ratio', min_value=0.0000, max_value=1.0,
                       value=0.35, step=0.0001, label_visibility='hidden')


# 如果不存在 'all_chosen_nodes'，在 session state 中初始化它
if 'all_chosen_nodes' not in st.session_state:
    st.session_state.all_chosen_nodes = []

if 'clear_signal' not in st.session_state:
    st.session_state.clear_signal = False

# 初始化 session state 变量
if 'click_result' not in st.session_state:
    st.session_state.click_result = None

# 确保 graph_node 和 graph_link 在 session_state 中持久化
if 'graph_node' not in st.session_state:
    st.session_state.graph_node = []
if 'graph_link' not in st.session_state:
    st.session_state.graph_link = []

company_type = pd.read_csv('Dataset/MC3/country-company_type.csv')
company_lable = pd.read_csv('Dataset/MC3/country-company_lable.csv')
company_revenue = pd.read_csv('Dataset/MC3/country-company_revenue.csv')
related2seafood = pd.read_csv('Dataset/MC3/country-company_related2seafood.csv')

nodes=pd.read_csv('Dataset/MC3/nodes.csv')
links=pd.read_csv('Dataset/MC3/links.csv')

# 优化后的数据处理函数
def process_heatmap_data(heatmap_choice):
    if heatmap_choice == 'country-company_type':
        data_df = company_type
    elif heatmap_choice == 'country-company_lable':
        data_df = company_lable
    elif heatmap_choice == 'country-company_revenue':
        data_df = company_revenue
    else:
        data_df = related2seafood

    data = [
        [col_index - 1, row_index, row[col_index]]
        for row_index, row in data_df.iterrows()
        for col_index in range(1, len(row))
    ]
    min_value = min(value for _, _, value in data)
    max_value = max(value for _, _, value in data)

    return data_df.keys()[1:], data_df['country'], data,data_df, min_value, max_value

# 根据用户的选择来处理数据
def process_data(data, log_scale):
    if log_scale:
        # Apply a logarithmic transformation to the third element of each list
        processed_data = [[x[0], x[1], np.log2(x[2])] if x[2] > 0 else [x[0], x[1], 0] for x in data]
        # Extract the third element from each sub-list for min and max calculation
        values = [x[2] for x in processed_data]
        # Calculate new min and max values
        min_value = min(values)
        max_value = max(values)
    else:
        processed_data = data
        # Extract the third element from each sub-list for min and max calculation
        values = [x[2] for x in data]
        # Use original min and max values
        min_value = min(values)
        max_value = max(values)
    return processed_data, min_value, max_value

main_container = st.container()
options_col, chart_col = main_container.columns((page_ratio, 1-page_ratio))

graph_node=[]
graph_link=[]


with options_col:
    heatmap_type = ['country-company_type',
                    'country-company_lable',
                    'country-company_revenue',
                    'country-related2seafood']
    heatmap_choice = st.selectbox("选择热力图类型:", heatmap_type)

    xaxis_labels, yaxis_labels, data, data_df,min_value, max_value = process_heatmap_data(heatmap_choice)

    col1, mid,col2 = st.columns(3)
    
    with col1:
        # 如果点击了“清除选中节点”按钮
        if st.button('Clear Selection'):
            st.session_state.all_chosen_nodes.clear()
            st.session_state.clear_signal = True  # 设置标志，指示需要忽略点击事件

    with col2:
        # 添加一个勾选框，用户可以选择是否应用对数尺度
        log_scale = st.checkbox('Log Color Scale')

    processed_data,min_value, max_value=process_data(data,log_scale)

    # 创建热力图
    heatmap = (
        HeatMap()
        .add_xaxis(list(xaxis_labels))
        .add_yaxis(
            series_name=heatmap_choice,
            yaxis_data=list(yaxis_labels),
            value=processed_data,
            label_opts=opts.LabelOpts(is_show=False, position="inside"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="HeatMap Example"),
            #标签样式
            tooltip_opts = opts.TooltipOpts(
                is_show=True,  # 是否显示提示框组件，包括提示框浮层和 axisPointer。
                trigger="item",  # 触发类型。'item' 表示数据项图形触发。
                position="inside",
                axis_pointer_type='cross',  # 使用十字准线指示器
                background_color="rgba(50,50,50,0.7)",  # 提示框浮层的背景颜色。
                border_color="#333",  # 提示框浮层的边框颜色。
                border_width=0,  # 提示框浮层的边框宽。
                textstyle_opts=opts.TextStyleOpts(color="#fff"),  # 提示框浮层的文本样式。
                formatter=JsCode("function(params){return params.value[2] + ' nodes';}") if not log_scale else(
                    JsCode(
                        """
                        function(params){
                            if (params.value[2] === 0) {
                                return '0'  + ' nodes';
                            } else {
                                return (2 ** params.value[2]).toFixed(0)  + ' nodes';
                            }
                        }
                        """
                    )
                )
            ),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                type_="none",  # 'line' | 'shadow' | 'none'
                
            ), 
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(font_size=10),
                position="bottom",
            ),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(font_size=10),
                position="left"),
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,  # 隐藏视觉映射控件
                min_=min_value,
                max_=max_value,
                is_calculable=True,
                orient="horizontal",
                pos_left="center",
                range_color=["#ffffff", "#000080"]  # 从白色到深蓝色
            )
        )
    )

    # 设置点击事件的JavaScript函数
    click_event_js = "function(params) {return params.data;}"

    # 渲染热力图并设置点击事件
    node_chosen = st_pyecharts(
        heatmap,
        events={"click": click_event_js},
        width="100%",
        height=700
    )
    
    # 当热力图被点击时，添加新节点到 session state
    if node_chosen and node_chosen not in st.session_state.all_chosen_nodes and st.session_state.clear_signal is False:
        st.session_state.all_chosen_nodes.append(node_chosen)

    # 如果清除信号被设置，则重置该信号
    if st.session_state.clear_signal:
        st.session_state.clear_signal = False

    st.write(st.session_state.all_chosen_nodes)

    with mid:
        # 如果点击了“添加到图表”按钮
        if st.button('Add to Graph'):
            #temp_chosen_nodes = st.session_state.all_chosen_nodes.copy()
            # st.session_state.all_chosen_nodes = []
            # st.session_state.clear_signal = True  # 设置标志，指示需要忽略点击事件
            

            # 遍历 node_chosen 列表
            for item in st.session_state.all_chosen_nodes:
                if isinstance(item, list) and len(item) == 3:
                    col_idx, row_idx, number = item
                    if number != 0:
                        selected_country = data_df.iloc[row_idx, 0]  # 国家信息在第0列
                        selected_company_type = data_df.columns[col_idx + 1]  # +1 因为我们跳过了第一列，它通常是索引列

                        filtered_df = nodes[(nodes['country'] == selected_country) & (nodes['company_type'] == selected_company_type)]
                        st.session_state.graph_node.extend(filtered_df['id'].tolist())
        
            # 去除重复的节点ID
            st.session_state.graph_node = list(set(st.session_state.graph_node))

            # # 打印结果将
st.write("graph_node:",st.session_state.graph_node)

# 定义类型到颜色的映射
type_color_mapping = {
    'Beneficial Owner': 'red',   # 请用实际的颜色代码替换 'color1'，例如 '#ff0000'
    'Company': 'yellow',            # 请用实际的颜色代码替换 'color2'，例如 '#00ff00'
    'Company Contacts': 'blue',   # 请用实际的颜色代码替换 'color3'，例如 '#0000ff'
}

# 创建节点类型列表
node_categories = [
    {"name": "Beneficial Owner", "itemStyle": {"color": "red"}},
    {"name": "Company", "itemStyle": {"color": "yellow"}},
    {"name": "Company Contacts", "itemStyle": {"color": "blue"}}
]

# 使用 chart_col 作为父容器来创建两个子容器
upper_chart_container = chart_col.container()
mid_chart_container=chart_col.container()
lower_chart_container = chart_col.container()

with upper_chart_container:
    #分为左右两部分，左边展示图，右边展示信息
    left_part,right_part=upper_chart_container.columns([2,1])

    with left_part:
        # 筛选出与 graph_node 相关的边
        filtered_links = links[links['source'].isin(st.session_state.graph_node) & links['target'].isin(st.session_state.graph_node)]

        # 准备节点和边的数据
        # 准备节点数据，为每个类型的节点设置不同的颜色
        nodes_data = [
            {
                "name": str(node['id']),
                "symbolSize": 10,
                "category": node['type'],  # 假设 nodes DataFrame 有一个 'type' 列
                "itemStyle": {"color": type_color_mapping.get(node['type'], 'default_color')}
            }
            for index, node in nodes.iterrows() if node['id'] in st.session_state.graph_node
        ]
        links_data = [{"source": str(row['source']), "target": str(row['target'])} for index, row in filtered_links.iterrows()]

        # 创建图表
        graph=Graph()
        graph.add("",
                nodes_data, 
                links_data,
                categories=node_categories,  # 添加 categories
                repulsion=4000)
        graph.set_global_opts(title_opts=opts.TitleOpts(title="Directed Graph"))

        # 设置点击事件的JavaScript函数
        click_event_js = "function(params) {return params.data;}"

        # 渲染有向图并设置点击事件
        result=st_pyecharts(graph,
                            events={"click": click_event_js},
                            height="400px", 
                            width="100%")
        
        # 检查点击事件的结果
        if result:
            st.session_state.click_result = result

        # 在右边的部分显示点击的节点信息
    with right_part:
        if st.session_state.click_result:
            # 提取被点击节点的ID
            clicked_node_id = st.session_state.click_result['name']
            
            # 在DataFrame中查找与该ID匹配的行
            node_details = nodes[nodes['id'] == clicked_node_id]
            
            # 如果找到匹配的节点，则显示其详细信息
            if not node_details.empty:
                st.subheader("Node Details")
                # 遍历DataFrame中的所有列，并显示每个列的信息
                for col in node_details.columns:
                    # 获取列的值，如果是空值则替换为字符串 "null"
                    value = node_details.iloc[0][col]
                    if pd.isna(value):  # 检查值是否为NaN或None
                        value = "null"
                    st.text(f"{col}: {value}")

with mid_chart_container:
    left,right=mid_chart_container.columns([1,1])

with left:
    Histogram_type = ['Country','Revenue','Label']
    Histogram_choice = st.selectbox("选择柱状图类型:", Histogram_type)

with right:
    # 添加一个勾选框，用户可以选择是否应用对数尺度
    log_scale2 = st.checkbox('Log Color Scale ')

country_count=pd.read_csv("Dataset/MC3/Country_count.csv")

with lower_chart_container:
    
    data=country_count
    # 根据log_scale2复选框的状态选择是否取对数
    if log_scale2:
        counts = np.log2(data['count']).tolist()  # 使用 log1p 来避免 log(0) 的问题
    else:
        counts = data['count'].tolist()

    # 创建直方图
    bar = Bar()
    bar.add_xaxis(data['country'].tolist())
    bar.add_yaxis("count", 
                counts,
                label_opts=opts.LabelOpts(is_show=False),
            )
    bar.set_global_opts(
        #title_opts=opts.TitleOpts(title="Country Count Histogram"),
        legend_opts=opts.LegendOpts(is_show=False),
        yaxis_opts=opts.AxisOpts(name="number"),#去掉网格线
        xaxis_opts=opts.AxisOpts(name="Country", 
                                 axislabel_opts=opts.LabelOpts(rotate=-15)),#x轴上标签旋转
        tooltip_opts=opts.TooltipOpts(
            is_show=True,
            trigger="axis",  # 当鼠标悬停在轴的时候显示
            axis_pointer_type="cross",  # 十字线指针
        ),
    )

    # 在 Streamlit 中渲染直方图
    st_pyecharts(bar, height="400px", width="100%")


