import streamlit as st
import os
from src import test_hypo, process as ps
from gsheetsdb import connect
import pandasql as psql
import pandas as pd
import io

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


def test_selector():

    df = pd.read_sql(
        f'SELECT * FROM "{sheet_url}"', conn)
    df = df.fillna('')

    responds = df.rename(columns=ps.column_loader(inverse=True))
    responds = responds[~(responds['L'] == '尚無投資經驗')]
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

        row0_1, row0_spacer2, row0_2 = st.columns(
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


def renderer():
    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
        (.1, 2, .2, 1, .1))

    row0_1.title('股票查詢系統')

    with row0_2:
        st.write('')

    row0_2.subheader(
        '2021 Fugle Customer Segmentation Analysis')

    row1_spacer1, row1_1, row1_spacer2 = st.columns((.1, 3.2, .1))

    with row1_1:
        st.markdown(
            "學習怎麼設置自己的股票查詢系統。以下結果不宜作為投資建議。其中**資產變化**一欄已經簡化為「以月為單位」，如需更改，請自行 Fork 加以修改。")
        st.markdown(
            "**請按照格式要求輸入值。可以輸入不同於預設的投資標的唷！** 👇🏾")

    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.columns(
        (.1, 1.5, 0.1, 1.5, 0.1))

    with row2_1:
        stock_id = st.text_input("輸入你的股票代碼*", '0050.TW')

        need_help = st.expander('需要幫忙嗎？ 👉')
        with need_help:
            st.markdown("""不知道您欲查詢的投資標的？只要搜尋「股票代碼.TW」就可以繼續查詢，如「0050.TW」。完整的台股代碼可以參考[本國上市證券國際證券辨識號碼一覽表](https: // isin.twse.com.tw/isin/C_public.jsp?strMode=2)。

有些上櫃公司的代碼需要加上「.TWO」。如果出現錯誤，請至[Yahoo! Finance](https: // finance.yahoo.com) 搜尋。""")

    with row2_2:
        capital = st.number_input("輸入本金", value=10000)

    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.columns(
        (.1, 1.5, 0.1, 1.5, 0.1))

    with row3_1:
        st.write('')

    with row3_2:
        st.write('')

    line1_spacer1, line1_1, line1_spacer2 = st.columns((.1, 3.2, .1))

    with line1_1:
        if capital == 0:
            st.write(
                "Looks like you did not want to invest in any money. Steal (Earn) some first before you start the analysis.")
            st.stop()
        st.write('')

    line2_spacer1, line2_1, line2_spacer2 = st.columns((.1, 3.2, .1))
    with line2_1:
        st.write('')

    st.write('')
    row4_space1, row4_1, row4_space2, row4_2, row4_space3 = st.columns(
        (.1, 1, .1, 1, .1))

    with row4_1:
        st.subheader('股票走勢')
        st.write('')

    with row4_2:
        st.subheader('股票成交量變化')

        st.write('sup')

    st.write('')
    row5_space1, row5_1, row5_space3 = st.columns(
        (.1, 2.1, .1))

    with row5_1:
        st.write('sup')

    row6_spacer1, row6_1, row6_spacer2 = st.columns((.1, 3.2, .1))
    with row6_1:
        st.markdown('***')
        st.markdown(
            "謝謝您瀏覽此小工具。此僅作為一個股票分析的簡單 Web App，如果您喜歡或願意一起開發更複雜的股票分析工具，請您聯繫我！")


def main():
    # Once we have the dependencies, add a selector for the app mode on the sidebar.
    st.sidebar.title("Channels")
    selector = ["All", "Public", "Fugle"]
    app_mode = st.sidebar.selectbox("Select a channel to continue",
                                    selector)

    if app_mode == selector[0]:
        st.sidebar.info('Still empty...')
    elif app_mode == selector[1]:
        test_selector()

        need_help = st.sidebar.expander(
            "🙋🏾‍♂️ Not sure what features are in our data?")
        with need_help:
            st.json(ps.column_loader())

    elif app_mode == selector[2]:
        st.sidebar.info('Still empty...')


if __name__ == '__main__':
    main()
