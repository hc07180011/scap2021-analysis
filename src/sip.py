import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from dateutil.relativedelta import relativedelta


@st.cache
def _month_range_day(installment, stock_df, start=None, end=None, offset=1):
    investment_dates_all = pd.date_range(start, end, freq='MS')
    investment_dates_all = investment_dates_all + \
        pd.tseries.offsets.DateOffset(days=offset-1)
    investment_dates = investment_dates_all[(
        investment_dates_all < stock_df.index[-1]) & (investment_dates_all > stock_df.index[0])]
    closest_investment_dates = stock_df.index.searchsorted(investment_dates)
    units_purchased = installment / \
        stock_df['Open'][closest_investment_dates]
    return closest_investment_dates, units_purchased


@st.cache
def compare_methods(stock_df, start, end, installment, offset=6):

    investment_dates, units_purchased = _month_range_day(
        installment, stock_df, start, end, offset=offset)
    lumpsum_amount = len(units_purchased) * installment
    total_units_purchased = sum(units_purchased)
    purchased_agg = units_purchased.copy()
    for i in range(1, len(purchased_agg)):
        purchased_agg[i] += purchased_agg[i - 1]
    sip_balance, sip_growth, sip_stats = stock_sip(
        stock_df, installment, investment_dates, lumpsum_amount, total_units_purchased, offset)
    lumpsum_balance, lumpsum_growth, lumpsum_stats = stock_lumpsum(
        stock_df, lumpsum_amount, investment_dates, lumpsum_amount /
        stock_df['Open'][0])
    return investment_dates, (sip_balance, sip_growth, sip_stats, purchased_agg), (lumpsum_balance, lumpsum_growth, lumpsum_stats)


@st.cache
def stock_sip(stock_df, installment, investment_dates, lumpsum_amount, total_units_purchased, offset=6):
    stock_daily_returns = stock_df['Adj Close'][investment_dates[0]:].ffill(
    ).pct_change()
    start = stock_daily_returns.index[0]
    end = stock_daily_returns.index[-1]
    # print(end)
    year_diff = relativedelta(end, start).years + \
        (relativedelta(end, start).months)/12

    init_balance = balance = installment
    total_balance = stock_daily_returns.copy()
    total_balance[0] = 0

    j = 0  # for investment_dates
    j_investment_dates = investment_dates - investment_dates[0]
    cost_df = pd.DataFrame()
    last_time = False
    for i in range(len(stock_daily_returns)):
        balance = balance * (1 + total_balance[i])
        if i == j_investment_dates[j] and i != 0:
            print(j_investment_dates[j], j)
            j += 1
            if (j >= len(j_investment_dates)) and last_time != True:
                j = len(j_investment_dates) - 1
                last_time = True

            balance += installment
        elif i == 0:
            j += 1

        if last_time:
            cost_df = cost_df.append(
                {'Cost': (j + 1) * installment}, ignore_index=True)
        else:
            cost_df = cost_df.append(
                {'Cost': (j) * installment}, ignore_index=True)

        total_balance[i] = balance
    cost_df.index = stock_daily_returns.index
    cost = cost_df.Cost
    daily_returns = stock_daily_returns * 100

    growth = pd.concat([daily_returns.rename("Return (%)"),
                        total_balance.rename("Balance"), cost.rename('Cost')], axis=1)
    returnRate = (total_balance[-1] - lumpsum_amount)/lumpsum_amount
    cgar = (((1+returnRate)**(1/year_diff))-1)
    stats = u'''
定期定額之後，您的總報酬率為 {:.2f}%。每個月 {} 號投資 **{}** 元，累積成本一共為 **{}** 元，到設定截止日期的市值為 **{:.2f}** 元。持有股數為 **{}** 股。

_開始日期_為 {}，_結束日期_為 {}\n，一共投資了 {:.2f} 年\n。這樣的年化報酬率 (%) 為 {:.2f}%\n'''.format(returnRate * 100, offset, installment, lumpsum_amount, total_balance[-1], total_units_purchased, start.date(), end.date(), year_diff, cgar * 100)
    return total_balance, growth, stats


@st.cache
def stock_lumpsum(stock_df, capital, investment_dates, total_units_purchased):
    stock_daily_returns = stock_df['Adj Close'][investment_dates[0]:].ffill(
    ).pct_change()
    start = stock_daily_returns.index[0]
    end = stock_df.index[-1]
    year_diff = relativedelta(end, start).years + \
        (relativedelta(end, start).months)/12

    init_balance = balance = capital

    total_balance = stock_daily_returns.copy()
    total_balance[0] = 0

    for i in range(len(stock_daily_returns)):
        balance = balance * (1+total_balance[i])
        total_balance[i] = balance

    daily_returns = stock_daily_returns * 100
    growth = pd.concat([daily_returns.rename("Return (%)"),
                        total_balance.rename("Balance")], axis=1)

    returnRate = (total_balance[-1] - total_balance[0])/total_balance[0]
    cgar = (((1+returnRate)**(1/year_diff))-1)
    stats = u'''
如果沒有定期定額投資，您的總報酬率為 {:.2f}%。本金一共是 {} 元，到設定截止日期的市值為 **{:.2f}** 元。持有股數為 **{}** 股。

_開始日期_為 {}，_結束日期_為 {}\n，一共投資了 {:.2f} 年\n。這樣的年化報酬率 (%) 為 {:.2f}%\n'''.format(returnRate * 100, capital, total_balance[-1], total_units_purchased, start.date(), end.date(), year_diff, cgar * 100)
    return total_balance, growth, stats


def main():

    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
        (.1, 2, .2, 1, .1))

    row0_1.title('定期定額股票查詢系統')

    with row0_2:
        st.write('')

    row0_2.subheader(
        'A Simple Stock Analysis App by [Brian L. Chen](https://icheft.github.io) (CHINESE VER.)')

    row1_spacer1, row1_1, row1_spacer2 = st.columns((.1, 3.2, .1))

    with row1_1:
        st.markdown(
            "定期定額投資成果查詢。")
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
        installment = st.number_input(
            "輸入定期定額金額", value=3000, step=1000, min_value=1000)

    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3, row3_3, row3_spacer4 = st.columns(
        (.1, 1, 0.05, 1, 0.05, 1, 0.1))

    with row3_1:
        start_date = st.date_input("開始日期", datetime.date(2000, 1, 1))

    with row3_2:
        end_date = st.date_input("結束日期", datetime.date.today())

    with row3_3:
        offset_day = int(st.selectbox('每月扣款日',
                                      ('6', '16', '26')))  # multichoice to be added

    line1_spacer1, line1_1, line1_spacer2 = st.columns((.1, 3.2, .1))

    with line1_1:
        if installment == 0:
            st.write(
                "Looks like you did not want to invest in any money. Steal (Earn) some first before you start the analysis.")
            st.stop()
        target = yf.Ticker(stock_id)
        stock_name = target.info['longName']
        st.header(f'分析 **{stock_name}**')
        start = start_date
        end = end_date
        stock_df = target.history(start=start, end=end, auto_adjust=False)
        investment_dates, (sip_balance, sip_growth, sip_stats, purchased_agg), (lumpsum_balance,
                                                                                lumpsum_growth, lumpsum_stats) = compare_methods(stock_df, start, end, installment, offset_day)

    line2_spacer1, line2_1, line2_spacer2 = st.columns((.1, 3.2, .1))
    with line2_1:
        # if stock_id.lower() != '0050.tw':
        #     compare_flag = st.checkbox("與大盤（0050.TW）比較？")
        # else:
        #     compare_flag = False
        compare_flag = False

    st.write('')
    row4_space1, row4_1, row4_space2, row4_2, row4_space3 = st.columns(
        (.1, 1, .1, 1, .1))

    with row4_1:
        st.subheader('股票走勢')
        if compare_flag == False:
            fig = px.line(stock_df['Close'][investment_dates[0]:], labels={
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
        st.subheader('股票持有股數變化')

        if compare_flag == False:
            fig = px.line(purchased_agg, labels={
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
            two_growth = pd.concat([sip_growth['Balance'].rename('定期定額'),
                                    lumpsum_growth['Balance'].rename('全部投入'), sip_growth['Cost'].rename('成本變化')], axis=1)

            fig = px.line(two_growth, labels={
                'value': 'Growth', 'variable': '項目名稱'})
            fig.update_layout(showlegend=True, margin={
                'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

            st.plotly_chart(fig, use_container_width=True)
            st.markdown('#### 定期定額')
            st.markdown(sip_stats)
            st.write('')

            st.markdown('#### 全部投入')
            st.markdown(lumpsum_stats)
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
