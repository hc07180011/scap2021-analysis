import streamlit as st
import os
from src import process as ps
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


def test_selector(include=False):

    df = pd.read_sql(
        f'SELECT * FROM "{sheet_url}"', conn)
    df = df.fillna('')

    responds = df.rename(columns=ps.column_loader(inverse=True))
    if not include:
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


def main():

    st.sidebar.title("Channels")
    selector = ["All", "Public", "Fugle"]
    app_mode = st.sidebar.selectbox("Select a channel to continue",
                                    selector)

    if app_mode == selector[0]:
        include = st.sidebar.checkbox(
            'Including everything! (Default 已篩選掉沒投資過的人)')
        test_selector(include=include)

        need_help = st.sidebar.expander(
            "🙋🏾‍♂️ Not sure what features are in our data?")
        with need_help:
            st.json(ps.column_loader())
    elif app_mode == selector[1]:
        include = st.sidebar.checkbox(
            'Including everything! (Default 已篩選掉沒投資過的人)')
        test_selector(include=include)

        need_help = st.sidebar.expander(
            "🙋🏾‍♂️ Not sure what features are in our data?")
        with need_help:
            st.json(ps.column_loader())

    elif app_mode == selector[2]:
        st.sidebar.info('Still empty...')


if __name__ == '__main__':
    main()
