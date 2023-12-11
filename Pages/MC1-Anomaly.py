import streamlit as st
import pandas as pd


st.set_page_config(page_title="FishEye", layout="wide",
                   page_icon=None, initial_sidebar_state="collapsed")

st.markdown("""
            <style>
            /* Removes padding, margin and set full height to the main content area */
            .main .block-container { 
                padding-top: 2rem; 
                padding-right: 1rem;
                padding-left: 2rem;
                padding-bottom: 0rem;
                margin: 0;
            }
            /* Additional custom styles can be added here */
            </style>
            """, unsafe_allow_html=True)

nodes = pd.read_csv('Dataset/MC1/Nodes.csv')
links = pd.read_csv('Dataset/MC1/Links.csv')


def _divider_():
    return st.markdown("""
        <style>
        .divider {
            margin-top: 0px; /* 上边距 */
            margin-bottom: 0px; /* 下边距 */
            border-color: #FF0000; /* 设置分割线颜色 */
            width: 100%;
        }
        </style>
        <hr class="divider"/>
    """, unsafe_allow_html=True)


col1, coll1, col2 = st.columns([2, 0.2, 5])

with col1:
    top_k = st.number_input("Top K Most Suspicious Nodes",
                            min_value=1, max_value=100, value=1, step=1)
    st.markdown('---')
    col01, col02 = st.columns([1, 1])
    with col01:
        min_com_threshold = st.number_input("Min ComAvgWt Threshold",
                                            min_value=0.0, max_value=1.0, value=0.0, step=0.001)
    with col02:
        max_com_threshold = st.number_input("Max ComAvgWt Threshold",
                                            min_value=0.0, max_value=100.0, value=0.0, step=0.001)
    slider1 = st.slider("Weight of Community", 0.0, 1.0,
                        step=0.01, key='slider1')
    _divider_()
    col11, col12 = st.columns([1, 1])
    with col11:
        min_rate_threshold = st.number_input("Min Rate Threshold",
                                             min_value=0.0, max_value=1.0, value=0.0, step=0.001)
    with col12:
        max_rate_threshold = st.number_input("Max Rate Threshold",
                                             min_value=0.0, max_value=100.0, value=0.0, step=0.001)
    slider2 = st.slider("Weight of Sigmod", 0.0, 1.0,
                        step=0.01, key='slider2')
    _divider_()
    slider3 = st.slider("Related To Location", 0.0, 1.0, step=0.01)
    _divider_()
    col41, col42 = st.columns([1, 1])
    with col41:
        min_node_threshold = st.number_input("Min NodeAvgWt Threshold",
                                             min_value=0.0, max_value=1.0, value=0.0, step=0.001)
    with col42:
        max_node_threshold = st.number_input("Max NodeAvgWt Threshold",
                                             min_value=0.0, max_value=1.0, value=0.0, step=0.001)
    slider4 = st.slider("Weight of Node", 0.0, 1.0,
                        step=0.01, key='slider4')
    _divider_()
    slider5 = st.slider("Weight of Power-law", 0.0, 1.0, step=0.01)
    _divider_()
    slider6 = st.slider("Related To Government", 0.0, 1.0, step=0.01)
    _divider_()
    slider7 = st.slider("If Size==0", 0.0, 1.0, step=0.01)

    score = dict()
    for i in range(len(nodes)):
        score[nodes.iloc[i]['id']] = 0

    def typeOfNode(id):
        for i in range(len(nodes)):
            if nodes.iloc[i]['id'] == id:
                return nodes.iloc[i]['type']

    for _, row in nodes.iterrows():
        # 社区平均权重
        if row['Community_avg_weight'] > max_com_threshold or rate < min_com_threshold:
            score[row['id']] += slider1

        # 出入度不平衡
        rate = row['In_Degree'] / \
            row['Out_Degree'] if row['Out_Degree'] != 0 else 100

        if rate > max_rate_threshold or rate < min_rate_threshold:
            score[row['id']] += slider2

        # 不与location相连
        if row['no_location'] == 1:
            score[row['id']] += slider3

        # 节点的平均权重
        if row['Average_Weight'] > max_node_threshold or rate < min_node_threshold:
            score[row['id']] += slider4

        # 幂律分布

        # 政府组织
        if row['Connected_political_organization'] == 1:
            score[row['id']] -= slider6

        # size==0
        if row['size'] == 0 or row['size'] == -1:
            score[row['id']] += slider7

with col2:
    st.subheader("Suspicious Set")
    show_df = nodes[nodes['id'].isin(st.session_state['sus_nodes1'])]
    st.data_editor(show_df)
    st.subheader("Suspicious Nodes")
    col11, col22 = st.columns([8, 1])

    st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 3em;           /* 设置按钮的高度 */
        margin-top: 0em;       /* 在按钮上方增加一些空间 */
        vertical-align: middle; /* 确保文字垂直居中 */
        line-height: 3em;      /* 通过行高来垂直居中按钮内的文字 */
    }
    </style>
    """, unsafe_allow_html=True)

    top_k_sus = [key for key, value in sorted(
        score.items(), key=lambda item: item[1], reverse=True)[:top_k]]
    for i in range(top_k):
        with col11:
            with st.expander(top_k_sus[i]):
                for index, row in nodes.iterrows():
                    if row['id'] == top_k_sus[i]:
                        for col in nodes.columns:
                            st.markdown(
                                f"<span style='font-size: 20px; color: #000000;'><b>{col}:</b></span>", unsafe_allow_html=True)
                            st.markdown(row[col])
                        break
        with col22:
            st.button('Add To Sus', on_click=lambda x=i: st.session_state['sus_nodes1'].add(
                top_k_sus[x]), key=str(i))
