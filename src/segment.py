import streamlit as st
import os
from src.component import convert_df
from src import process as ps
from gsheetsdb import connect
import pandasql as psql
import pandas as pd
import io
import numpy as np
import plotly.express as px

profile_dict = {
    '初步篩選': [],
    '大鯨魚: 3000 萬以上': [0],
    '競爭對手的客戶: 有在用永豐 + 實際寫過 API': [2, 6],
    'Ideal 客戶 I - 分或小時交易: 200-1000 萬成交量 + 分或小時交易 + 會寫程式 + 沒有實際用過 API': [3, 4, 7, 5],
    'Ideal 客戶 II - 日交易: 200-1000 萬成交量 + 日交易 + 會寫程式 + 沒有實際用過 API': [3, 1, 7, 5],
}


def bar_with_data(data: np.ndarray, x_name: str, y_name: str) -> None:

    value_counts = dict()
    for val in data:
        for v in val.split("\n"):  # Survey Cake format
            if v not in value_counts:
                value_counts[v] = 1
            else:
                value_counts[v] += 1

    if "其他" not in value_counts:
        value_counts["其他"] = 0

    # 把有「其他」的都算一起
    for k in value_counts:
        if k != "其他" and "其他" in k:
            value_counts["其他"] += value_counts[k]
            value_counts[k] = 0

    # 刪掉 count 是 0 的
    value_counts = dict({k: v for k, v in value_counts.items() if v})

    # 排序，並 truncate 以及算比例
    counts = list([
        v
        for _, v in sorted(value_counts.items(), key=lambda item: -item[1])
    ])
    keys = list([
        "{} ({}%)".format(
            (k if len(k) < 10 else "{} ...".format(
                k[:10])) if k != "nan" else "未填答",
            round(v / len(data) * 100, 2)
        )
        for k, v in sorted(value_counts.items(), key=lambda item: -item[1])
    ])

    dummy_dict = {x_name: [], y_name: []}
    for i in range(len(counts)):
        dummy_dict[x_name].append(keys[i])
        dummy_dict[y_name].append(counts[i])
    fig = px.bar(dummy_dict, x=x_name, y=y_name, title=x_name.upper())
    fig.update_layout(margin=dict(b=0, l=0, r=0))

    return fig


def get_dict(table_name: str) -> dict:

    return {
        0: f"select * from {table_name} where P LIKE '3,000%';",
        1: f"select * from {table_name} where O LIKE '日%';",
        2: f"select * from {table_name} where A LIKE '實際寫過程式%';",
        3: f"select * from {table_name} where P LIKE '201%';",
        4: f"select * from {table_name} where O LIKE '分、小時%';",
        5: f"select * from {table_name} where A NOT LIKE '實際寫過程式%';",
        6: f"select * from {table_name} where I LIKE '%永豐%';",
        7: f"select * from {table_name} where T NOT LIKE '完全沒寫過%';",
        8: f"select * from {table_name} where A LIKE '使用過套裝軟體%';",
        9: f"select * from {table_name} where M = '是';",
        10: f"select * from {table_name} where P LIKE '51%';",
        11: f"select * from {table_name} where P LIKE '50%';",
        12: f"select * from {table_name} where P LIKE '51%' OR P LIKE '201%'"
    }


def sidebar_helper():
    st.sidebar.success('testing')
    pass


def default_ta():
    option = st.selectbox(
        'Choose a profile to continue',
        [key for key in profile_dict.keys()])
    return profile_dict[option]


def custom_feature_form():
    customized = st.expander('Need custom input? 👉🏽')
    features = [False for f in range(13)]
    return_obj = None
    with customized:
        with st.form("criteria_form"):
            st.write("Custom Features（我們選出的 criteria - 選項皆為 `AND`）")

            row1_1, row1_2, row1_3 = st.columns((1, 1, 1))
            with row1_1:
                features[0] = st.checkbox('月交易量 3000 萬以上')
            with row1_2:
                features[1] = st.checkbox('日交易')
            with row1_3:
                features[2] = st.checkbox('有使用過 API trading')

            row2_1, row2_2, row2_3 = st.columns((1, 1, 1))
            with row2_1:
                features[3] = st.checkbox('月交易量 200-1000 萬')
            with row2_2:
                features[4] = st.checkbox('分、小時交易')
            with row2_3:
                features[5] = st.checkbox('沒使用過 API 做交易')

            row3_1, row3_2, row3_3 = st.columns((1, 1, 1))
            with row3_1:
                features[6] = st.checkbox('有在用永豐的人')
            with row3_2:
                features[7] = st.checkbox('有基本程式能力')
            with row3_3:
                features[8] = st.checkbox('僅用過套裝軟體')

            row4_1, row4_2, row4_3 = st.columns((1, 1, 1))
            with row4_1:
                features[9] = st.checkbox('擁有 Portfolio 且有五隻股票以上')
            with row4_2:
                features[10] = st.checkbox('月交易量 51-200 萬')
            with row4_3:
                features[11] = st.checkbox('月交易量 50 萬以下')

            features[12] = st.checkbox('月交易量 51-1000 萬')

            submitted = st.form_submit_button("Submit")
            if submitted:
                return_obj = features

        st.markdown("""
                    <center>OR</center>
                    <br/>""", unsafe_allow_html=True)

        with st.form("query_form"):
            st.markdown("自訂 query (table name = `output_df`)")

            query = st.text_area(
                'Custom Query (in SQL)', 'SELECT * FROM output_df;')
            submitted = st.form_submit_button("Submit")
            if submitted:
                return_obj = query

        return return_obj


def runner(df: pd.DataFrame):
    ta_criteria = default_ta()
    output_df = df.copy()
    ori_len = len(output_df)
    custom_feature = custom_feature_form()
    output_df = psql.sqldf(
        'select * from output_df;', locals())
    if custom_feature is not None:
        st.success(f'✍️ 使用 custom profile')
        query_dict = get_dict('output_df')
        if type(custom_feature) is not str:
            for i in range(len(custom_feature)):
                if custom_feature[i]:
                    output_df = psql.sqldf(
                        query_dict[i], locals())
        else:
            output_df = psql.sqldf(
                custom_feature, locals())

    else:
        st.success(f'✍️ 使用 default profile')
        query_dict = get_dict('output_df')
        for c in ta_criteria:
            output_df = psql.sqldf(
                query_dict[c], locals())

    st.markdown(
        f'''{len(output_df)} out of {ori_len} ({round(len(output_df) / ori_len * 100, 2)}%)''')
    st.write(output_df.head())
    st.download_button(
        label=f"📓 Download (.csv)",
        data=convert_df(output_df),
        file_name=f'output.csv',
        mime='text/csv',
    )

    # final target customer traits
    st.markdown('## User Profile')
    row1_1, row1_2 = st.columns(
        (1, 1))
    with row1_1:
        fig = px.bar(output_df.groupby('X').agg(
            'size').reset_index(), x='X', y=0, labels={
            '0': 'Count', 'X': 'Age'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)
    with row1_2:
        fig = px.bar(output_df.groupby('W').agg(
            'size').reset_index(), x='W', y=0, labels={
            '0': 'Count', 'W': 'Gender'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    row2_1, row2_2 = st.columns(
        (1, 1))
    with row2_1:
        fig = px.bar(output_df.groupby('P').agg(
            'size').reset_index(), x='P', y=0, labels={
            '0': 'Count', 'P': 'Frequency'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)
    with row2_2:
        fig = px.bar(output_df.groupby('O').agg(
            'size').reset_index(), x='O', y=0, labels={
            '0': 'Count', 'O': 'Frequency'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    row3_1, row3_2 = st.columns(
        (1, 1))
    with row3_1:
        study_background = [
            '商管/人文/社會相關 (e.g. 企管、財會、歷史、哲學等)', '資訊/工程/數理相關 (e.g.資工、電機、資管、土木、機械、化工等)', '醫學/生物/農業相關 (e.g. 醫科、護理、森林、生科等)', '藝術/傳播相關 (e.g. 傳播、音樂、設計等)']
        sb_cnt = dict()
        for val in output_df['Y']:
            for ch in study_background:
                if ch in val:
                    if ch not in sb_cnt:
                        sb_cnt[ch] = 1
                    else:
                        sb_cnt[ch] += 1
        sb_dict = {'Background': [], 'Count': []}
        for key, value in sb_cnt.items():
            sb_dict['Background'].append(key)
            sb_dict['Count'].append(value)
        fig = px.bar(sb_dict, x='Background', y='Count')
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    with row3_2:
        fig = px.bar(output_df.groupby('Z').agg(
            'size').reset_index(), x='Z', y=0, labels={
            '0': 'Count', 'Z': 'Occupation'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    st.markdown('#### Channels')

    learn_investment_ch = ['資訊平台（如鉅亨網、 Investing.com、 Tradingview 等',
                           'Podcast', '券商', 'YouTuber', '新聞（如 Yahoo 新聞、實體報紙、 LineToday 等）', '書籍', '自行 Google', '社群平台']

    learn_coding_ch = ['國內線上學習平台（如量化通、HaHow 等）', '看 Medium 文章',
                       '閱讀書籍', '國外線上學習平台（如 Cousera、Udemy、edX 等）', 'YouTube 頻道', '學校上課']

    # this is probably the dumbest way, but I am not in the stackoverflow mode
    lich_cnt = dict()
    for val in output_df['R']:
        for ch in learn_investment_ch:
            if ch in val:
                if ch not in lich_cnt:
                    lich_cnt[ch] = 1
                else:
                    lich_cnt[ch] += 1
    lcch_cnt = dict()
    for val in output_df['V']:
        for ch in learn_coding_ch:
            if ch in val:
                if ch not in lcch_cnt:
                    lcch_cnt[ch] = 1
                else:
                    lcch_cnt[ch] += 1

    lcch_dict = {'Channel': [], 'Count': []}
    for key, value in lcch_cnt.items():
        lcch_dict['Channel'].append(key)
        lcch_dict['Count'].append(value)

    lich_dict = {'Channel': [], 'Count': []}
    for key, value in lich_cnt.items():
        lich_dict['Channel'].append(key)
        lich_dict['Count'].append(value)

    row4_1, row4_2 = st.columns(
        (1, 1))
    with row4_1:
        st.write('程式學習管道')
        fig = px.bar(lcch_dict, x='Channel', y='Count')
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    with row4_2:
        st.write('投資理財管道')
        fig = px.bar(lich_dict, x='Channel', y='Count')
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    load_more_charts = st.checkbox('要載入全部圖檔嗎？ (會吃大量記憶體噢 🥵)')
    if load_more_charts:
        more_chart = st.expander('More charts 🙈')

        with more_chart:
            for key in output_df.columns[:-10]:
                if key == "id":
                    # Skip first col
                    continue
                try:
                    st.plotly_chart(bar_with_data(
                        output_df[key].to_numpy().flatten(),
                        x_name=ps.column_loader()[key],
                        y_name='Frequency'
                    ), use_container_width=True)
                except:
                    st.write(f'{ps.column_loader()[key]} ({key}) is skipped.')
