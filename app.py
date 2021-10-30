import streamlit as st
import os
from src import process as ps
from gsheetsdb import connect
import pandasql as psql
import pandas as pd
import io
import plotly.express as px

DEPLOY_TO_HEROKU = True

EMOJI_URL = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/282/chart-increasing_1f4c8.png"

# Set page title and favicon.
st.set_page_config(
    page_title="2021 SCAP <> Fugle Market Segmentation", page_icon=EMOJI_URL, layout="wide"
)

conn = connect()

if not DEPLOY_TO_HEROKU:
    sheet_url = st.secrets["public_gsheets_url"]
else:
    sheet_url = os.environ['PUBLIC_GSHEETS_URL']

mode_selector = ["All", "Public", "Fugle"]
method_selector = ["Hypo Querying", "Hypo Testing - Funnel"]


def pysqldf(q): return psql.sqldf(q, globals())


# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    return rows


@st.cache(ttl=600)
def pd_run_query(query):
    df = pd.read_sql(query, conn)
    return df


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(encoding='utf_8_sig')


@st.cache()
def load_df(include=False):
    df = pd.read_sql(
        f'SELECT * FROM "{sheet_url}"', conn)
    df = df.fillna('')

    responds = df.rename(columns=ps.column_loader(inverse=True))
    if not include:
        responds = responds[~(responds['L'] == '尚無投資經驗')]
    return responds


def test_selector(include=False):
    responds = load_df(include)
    global_len = len(responds)

    custom_query = st.expander('Need Custom Query?')
    with custom_query:
        st.markdown("""Notes:
+ Table Name is `responds`
+ You can see all the features (columns) in the sidebar by pressing that bling bling expander ✨
<br/><br/>""", unsafe_allow_html=True)

        query_hypo_txt = st.text_input('Your Hypothesis', '假說').strip()
        query = st.text_area(label='Enter Your Query', value='''-- 21-40歲 + 注重效率 + 有台股交易需求
SELECT *
FROM   responds
WHERE  (`X` = '21-30歲' OR `X` = '31-40歲')
AND    `D` LIKE '%能省去大量觀盤及執行交易的時間%'
AND    `N` LIKE '%台股市場%';''', height=180)

        output_df = psql.sqldf(
            query, locals())\
            .rename(columns=ps.column_loader(inverse=False))
        st.markdown(
            f'''### {query_hypo_txt}
({len(output_df)} out of {global_len} - {round(len(output_df)/global_len * 100,2)}%)''')
        st.write(output_df)

        row0_1, _, row0_2 = st.columns(
            (1.2, .1, 1.2))

        with row0_1:
            st.download_button(
                label=f"📓 Download ({query_hypo_txt}.csv)",
                data=convert_df(output_df),
                file_name=f'{query_hypo_txt}.csv',
                mime='text/csv',
            )
        with row0_2:
            st.download_button(
                label=f"🧑🏾‍💻 Download ({query_hypo_txt}.sql)",
                data=query,
                file_name=f'{query_hypo_txt}.sql',
                mime='text/plain',
            )
        st.markdown("***")

    for sql_path in list([x for x in os.listdir("sql/b") if x[-4:] == ".sql"]):
        if sql_path == "schema.sql":
            continue

        output_df = psql.sqldf(
            open(os.path.join("sql/b", sql_path), "r").read(), locals())\
            .rename(columns=ps.column_loader(inverse=False))
        hypo_txt = open(os.path.join("sql/b", sql_path),
                        "r").readlines()[0][3:].strip()
        st.markdown(
            f'''### {hypo_txt}
({len(output_df)} out of {global_len} - {round(len(output_df)/global_len * 100,2)}%)''')
        st.write(output_df)

        st.download_button(
            label=f"📓 Download ({hypo_txt}.csv)",
            data=convert_df(output_df),
            file_name=f'{hypo_txt}.csv',
            mime='text/csv',
        )


def ta_funnel(include=False):
    # target audience funnel testing
    responds = load_df(include).reset_index(drop=True)
    global_len = len(responds)

    # 解決痛點：程式能力不足、覺得安裝或申請麻煩的人、沒聽過但回答「是」的人、認為「我認為此券商的產品本身系統穩定度夠、具有技術支援、響應時間短」重要的人

    st.markdown("""## #1 Pain
解決痛點 (things that Fugle possesses)：

+ 程式能力不足
+ 覺得安裝或申請麻煩的人
+ 沒聽過但回答「是」的人
+ 認為「我認為此券商的產品本身系統穩定度夠、具有技術支援、響應時間短」重要的人
""")

    query1 = """select * from responds
where ((C like '%程式能力不足'
or C like '%安裝及申請%') and C <> '')
or H like '是'
or (J not like '我認為此券商的產品本身系統穩定度夠、具有技術支援、響應時間短' and J <> '');
    """
    output_df = psql.sqldf(query1, locals())
    q1_cnt = len(output_df)

    row1_1, row1_2 = st.columns(
        (4.5, 1.5))
    with row1_1:
        fig = px.sunburst(output_df, path=['A', 'T'])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    with row1_2:
        st.markdown(
            f'{len(output_df)} ({round(len(output_df) / global_len * 100, 2)}%)')
        st.write(output_df)

    st.markdown('## #2 Pain + Fit (市場為台股)')

    query2 = """select * from output_df
where N like '台%';
    """
    output_df = psql.sqldf(query2, locals())
    q2_cnt = len(output_df)

    row2_1, row2_2 = st.columns(
        (4.5, 1.5))
    with row2_1:
        fig = px.sunburst(output_df, path=['A', 'T'])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    with row2_2:
        st.markdown(
            f'{len(output_df)} ({round(len(output_df) / q1_cnt * 100, 2)}%)')
        st.write(output_df)

    st.markdown("""## #3 Pain + Fit + Ready
+ 已經在寫 Python or Node 的人
+ 不能是完全沒寫過程式的人
+ 有自己的 portfolio 應該會馬上可以體驗到
""")

    query3 = """select * from output_df
where U like 'Python' or U like '%Node%'
and T not like '完全沒寫%'
and M = '是';
    """
    output_df = psql.sqldf(query3, locals())
    q3_cnt = len(output_df)

    st.markdown(
        f'{len(output_df)} ({round(len(output_df) / q2_cnt * 100, 2)}%)')
    st.write(output_df)

    # final target customer traits
    st.markdown('## Target Customers')
    row4_1, row4_2 = st.columns(
        (1, 1))
    with row4_1:
        fig = px.bar(output_df.groupby('X').agg(
            'size').reset_index(), x='X', y=0, labels={
            '0': 'Count', 'X': 'Age'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)
    with row4_2:
        fig = px.bar(output_df.groupby('W').agg(
            'size').reset_index(), x='W', y=0, labels={
            '0': 'Count', 'W': 'Gender'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(output_df.groupby('P').agg(
        'size').reset_index(), x='P', y=0, labels={
        '0': 'Count', 'P': 'Frequency'})
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(output_df.groupby('O').agg(
        'size').reset_index(), x='O', y=0, labels={
        '0': 'Count', 'O': 'Frequency'})
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

    st.plotly_chart(fig, use_container_width=True)

    row5_1, row5_2 = st.columns(
        (1, 1))
    with row5_1:
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

    with row5_2:
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

    row5_1, row5_2 = st.columns(
        (1, 1))
    with row5_1:
        st.write('程式學習管道')
        fig = px.bar(lcch_dict, x='Channel', y='Count')
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)

    with row5_2:
        st.write('投資理財管道')
        fig = px.bar(lich_dict, x='Channel', y='Count')
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

        st.plotly_chart(fig, use_container_width=True)


def sidebar_helper(app_method=method_selector[0]):
    # ["Hyp Querying", "Hypo Testing - Funnel"]
    include = st.sidebar.checkbox(
        'Including everything! (Default 已篩選掉沒投資過的人)')

    if app_method == method_selector[0]:
        test_selector(include=include)
    elif app_method == method_selector[1]:
        ta_funnel(include=include)

    need_help = st.sidebar.expander(
        "🙋🏾‍♂️ Not sure what features are in our data?")
    with need_help:
        st.json(ps.column_loader())


def main():

    st.sidebar.title("Channels")
    app_mode = st.sidebar.selectbox("Select a channel to continue",
                                    mode_selector)

    app_method = st.sidebar.selectbox("Select a testing method to continue",
                                      method_selector)

    if app_mode == mode_selector[0]:
        sidebar_helper(app_method)
    elif app_mode == mode_selector[1]:
        sidebar_helper(app_method)
    elif app_mode == mode_selector[2]:
        st.sidebar.info('Still empty...')


if __name__ == '__main__':
    main()
