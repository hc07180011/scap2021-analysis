import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.graph_objs as go


def _max_width_():
    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )


@st.cache
def stock_analyzer(stock_id, capital, start_date, end_date, compare=False):
    if compare == True:
        stock_0050 = yf.Ticker('0050.TW')
        stock_df_0050 = stock_0050.history(
            start=start_date, end=end_date, auto_adjust=False)
        stock_monthly_returns_0050 = stock_df_0050['Adj Close'].resample(
            'M').ffill().pct_change()
        start_0050 = stock_monthly_returns_0050.index[0]
        end_0050 = stock_df_0050.index[-1]  # 以 stock 的最後一天為結束日期.
        year_diff_0050 = relativedelta(end_0050, start_0050).years + \
            (relativedelta(end_0050, start_0050).months)/12

        init_balance_0050 = balance_0050 = capital
        total_balance_0050 = stock_monthly_returns_0050.copy()
        total_balance_0050[0] = 0

        for i in range(len(stock_monthly_returns_0050)):
            balance_0050 = balance_0050 * (1+total_balance_0050[i])
            total_balance_0050[i] = balance_0050

        monthly_returns_0050 = stock_monthly_returns_0050 * 100
        growth_0050 = pd.concat([monthly_returns_0050.rename("Return (%)"),
                                 total_balance_0050.rename("Balance")], axis=1)

        returnRate_0050 = (
            total_balance_0050[-1] - total_balance_0050[0])/total_balance_0050[0]
        cgar_0050 = (((1+returnRate_0050)**(1/year_diff_0050))-1)
        precise_start = stock_df_0050.index[0]
        precise_end = stock_df_0050.index[-1]

    stock_obj = yf.Ticker(stock_id)
    if compare == True:
        start = precise_start
        end = precise_end
    else:
        start = start_date
        end = end_date
    stock_df = stock_obj.history(start=start, end=end, auto_adjust=False)

    stock_monthly_returns = stock_df['Adj Close'].resample(
        'M').ffill().pct_change()
    start = stock_monthly_returns.index[0]
    end = stock_df.index[-1]  # 以 stock 的最後一天為結束日期.
    year_diff = relativedelta(end, start).years + \
        (relativedelta(end, start).months)/12

    init_balance = balance = capital
    total_balance = stock_monthly_returns.copy()
    total_balance[0] = 0

    for i in range(len(stock_monthly_returns)):
        balance = balance * (1+total_balance[i])
        total_balance[i] = balance

    monthly_returns = stock_monthly_returns * 100
    growth = pd.concat([monthly_returns.rename("Return (%)"),
                        total_balance.rename("Balance")], axis=1)

    returnRate = (total_balance[-1] - total_balance[0])/total_balance[0]
    cgar = (((1+returnRate)**(1/year_diff))-1)
    stats = ["", ""]
    stats[0] = u'''
您的總報酬率為 {:.2f}%。由本金 **{}** 元到設定截止日期的市值為 **{:.2f}** 元。

_開始日期_為 {}，_結束日期_為 {}\n，一共投資了 {:.2f} 年\n。這樣的年化報酬率 (%) 為 {:.2f}%\n'''.format(returnRate * 100, init_balance, init_balance * (1 + returnRate), start.date(), end.date(), year_diff, cgar * 100)
    if compare:
        stats[1] = u'''
與大盤相比，您的總報酬率為 {:.2f}%，而大盤為 {:.2f}%。若當初投資 0050，則會由本金 **{}** 元到設定截止日期的市值為 **{:.2f}** 元。而您目前的市值為 **{:.2f}** 元。

_開始日期_為 {}，_結束日期_為 {}\n，一共投資了 {:.2f} 年\n。大盤的年化報酬率 (%) 為 {:.2f}%，而您的投資標的為 {:.2f}%。\n'''.format(returnRate * 100, returnRate_0050 * 100, init_balance_0050, init_balance_0050 * (1 + returnRate_0050), init_balance * (1 + returnRate), start.date(), end.date(), year_diff_0050, cgar_0050 * 100, cgar * 100)

        stock_df = [stock_df, stock_df_0050]
        growth = [growth, growth_0050]

    return stock_df, growth, stats


def main():

    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
        (.1, 2, .2, 1, .1))

    row0_1.title('股票查詢系統')

    with row0_2:
        st.write('')

    row0_2.subheader(
        'A Simple Stock Analysis App by [Brian L. Chen](https://icheft.github.io) (CHINESE VER.)')

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
            st.markdown("""不知道您欲查詢的投資標的？只要搜尋「股票代碼.TW」就可以繼續查詢，如「0050.TW」。完整的台股代碼可以參考[本國上市證券國際證券辨識號碼一覽表](https://isin.twse.com.tw/isin/C_public.jsp?strMode=2)。

有些上櫃公司的代碼需要加上「.TWO」。如果出現錯誤，請至 [Yahoo! Finance](https://finance.yahoo.com) 搜尋。""")

    with row2_2:
        capital = st.number_input("輸入本金", value=10000)

    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.columns(
        (.1, 1.5, 0.1, 1.5, 0.1))

    with row3_1:
        start_date = st.date_input("開始日期", datetime.date(2000, 1, 1))

    with row3_2:
        end_date = st.date_input("結束日期", datetime.date.today())

    line1_spacer1, line1_1, line1_spacer2 = st.columns((.1, 3.2, .1))

    with line1_1:
        if capital == 0:
            st.write(
                "Looks like you did not want to invest in any money. Steal (Earn) some first before you start the analysis.")
            st.stop()
        target = yf.Ticker(stock_id)
        stock_name = target.info['longName']
        st.header(f'分析 **{stock_name}**')

    line2_spacer1, line2_1, line2_spacer2 = st.columns((.1, 3.2, .1))
    with line2_1:
        if stock_id.lower() != '0050.tw':
            compare_flag = st.checkbox("與大盤（0050.TW）比較？")
        else:
            compare_flag = False

    st.write('')
    row4_space1, row4_1, row4_space2, row4_2, row4_space3 = st.columns(
        (.1, 1, .1, 1, .1))

    stock_df, growth, stats = stock_analyzer(
        stock_id, capital, start_date, end_date, compare=compare_flag)

    with row4_1:
        st.subheader('股票走勢')
        if compare_flag == False:
            fig = px.line(stock_df['Close'], labels={
                'Date': 'Date', 'value': 'Stock Price'}, hover_data={'variable': False})
            fig.update_layout(showlegend=False, margin={
                'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
        else:
            stock_close = []
            stock_close.append(stock_df[0]['Close'].rename(stock_id))
            stock_close.append(stock_df[1]['Close'].rename('0050.TW'))
            stock_close = pd.concat(stock_close, axis=1)
            fig = px.line(stock_close, labels={
                'value': 'Growth', 'variable': 'Stock ID'})
            fig.update_layout(
                margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='x')

        st.plotly_chart(fig, use_container_width=True)

    with row4_2:
        st.subheader('股票成交量變化')

        if compare_flag == False:
            fig = px.line(stock_df['Volume'], labels={
                'Date': 'Date', 'value': 'Volume'}, hover_data={'variable': False})
            fig.update_layout(showlegend=False, margin={
                'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
        else:
            stock_Volume = []
            stock_Volume.append(stock_df[0]['Volume'].rename(stock_id))
            stock_Volume.append(stock_df[1]['Volume'].rename('0050.TW'))
            stock_Volume = pd.concat(stock_Volume, axis=1)
            fig = px.line(stock_Volume, labels={
                'value': 'Growth', 'variable': 'Stock ID'})
            fig.update_layout(
                margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='x')

        st.plotly_chart(fig, use_container_width=True)

    st.write('')
    row5_space1, row5_1, row5_space3 = st.columns(
        (.1, 2.1, .1))

    with row5_1:
        st.subheader('資產變化')
        if compare_flag == False:
            fig = px.line(growth['Balance'], labels={
                'Date': 'Date', 'value': 'Growth'}, hover_data={'variable': False})
            fig.update_layout(showlegend=False, margin={
                'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

            st.plotly_chart(fig, use_container_width=True)
            st.markdown(stats[0])
        else:
            ind_growth = []
            ind_growth.append(growth[0]['Balance'].rename(stock_id))
            ind_growth.append(growth[1]['Balance'].rename('0050.TW'))
            ind_growth = pd.concat(ind_growth, axis=1)
            fig = px.line(ind_growth, labels={
                'value': 'Growth', 'variable': 'Stock ID'})
            fig.update_layout(
                margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='x')

            st.plotly_chart(fig, use_container_width=True)
            st.markdown(stats[1])

    row6_spacer1, row6_1, row6_spacer2 = st.columns((.1, 3.2, .1))
    with row6_1:
        st.markdown('***')
        st.markdown(
            "謝謝您瀏覽此小工具。此僅作為一個股票分析的簡單 Web App，如果您喜歡或願意一起開發更複雜的股票分析工具，請您聯繫我！")


if __name__ == '__main__':
    main()
