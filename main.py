import os
import pickle
import sqlite3
import tempfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


font = FontProperties(fname=os.path.join("tools", "DFLiHei-Bd.ttc"))


def column_loader() -> dict:
    return dict({
        "id": "id",
        "A": "於填寫這份問卷之前，您對於「串接 API 程式執行程式交易」的理解及使用經驗為何？",
        "B": "您為何會選擇套裝軟體執行程式交易？",
        "C": "為何不想或尚未開始串接 API 程式交易？",
        "D": "您為何會選擇執行 API 交易？",
        "E": "您目前使用的交易 API 為何種類型？",
        "F": "目前於哪個平台進行與串接 API 相關的投資行為？",
        "G": "當提到台股 API 產品，您會想到哪些券商所提供的 API？",
        "H": "簡單來說，程式交易有以下幾個優點：處理大量資料並同時操作 3 檔以上的股票由程式判斷買賣點，不因情緒或直覺造成遲疑程式能自動幫您看盤並執行交易，省去大量時間以歷史數據回測交易策略，按績效優化交易策略了解程式交易四個優點後，根據您目前的交易習慣，是否有意願嘗試使用？",
        "I": "您目前是使用台股哪（幾）間券商所提供的 API？",
        "J": "為甚麼您會選擇此券商執行程式交易 API ?",
        "K": "基於您對程式交易 API 的理解，下列何者最能吸引您使用證券交易API ?",
        "L": "您有幾年的投資經驗？",
        "M": "您是否有建立自己的投資組合（portfolio），且該組合有 5 支股票以上？",
        "N": "您目前於哪些市場進行投資交易？",
        "O": "您進行投資交易時，大概多久交易一次 ?",
        "P": "您目前每月交易量（新台幣）大約多少？",
        "Q": "您投資交易時最經常採行的交易策略為何？ ",
        "R": "您平常接收投資理財相關資訊的來源為何？",
        "S": "您有在使用的作業系統有哪些？",
        "T": "您寫程式的經驗為何?",
        "U": "您習慣使用的程式語言有哪些？",
        "V": "若您有精進程式能力需求，會透過哪些渠道去學習？",
        "W": "您的性別",
        "X": "您的年齡",
        "Y": "教育背景",
        "Z": "目前職業",
        "AA": "其他",
        "AB": "問卷發放後，我們將於後續邀請合適人選進一步訪談，對參與訪談的受訪者，我們會給予現金新台幣 500 元作為小回饋。請問您是否有意願參與後續的訪談，讓我們更加瞭解您對證券交易 API 的使用需求？",
        "AC": "請問是否願意提供您的 Email？",
        "AD": "填答時間",
        "AE": "填答秒數",
        "AF": "IP紀錄",
        "AG": "額滿結束註記",
        "AH": "使用者紀錄",
        "AI": "會員時間",
        "AJ": "會員編號",
        "AK": "自訂ID",
        "AL": "備註"
    })


def data_preprocessing(data_dir: str = "data") -> sqlite3.Connection:
    os.makedirs(data_dir, exist_ok=True)
    csv_paths = os.listdir(data_dir)

    df = pd.DataFrame({})
    for path in list([x for x in csv_paths if ".csv" in x]):
        df = df.append(
            pd.read_csv(
                os.path.join(data_dir, path),
                encoding="utf-8"
            ),
            ignore_index=True
        )
    
    if not len(df):
        raise FileNotFoundError

    os.remove("fugle.db")
    con = sqlite3.connect("fugle.db")

    cur = con.cursor()
    with open(os.path.join("sql", "schema.sql"), "r") as f:
        cur.execute(f.read())

    for i in range(len(df)):
        cur.execute(
            "INSERT INTO responds VALUES ({},\"{}\")".format(
                i, "\",\"".join([str(x) for x in df.loc[i, :].to_numpy()])
            )
        )

    con.commit()
    return con


def plot_pie_with_raw_data(data: np.ndarray, column_names: dict, title: str, output_dir: str) -> None:

    value_counts = dict()
    for val in data:
        for v in val.split("\n"): # Survey Cake format
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
            (k if len(k) < 10 else "{} ...".format(k[:10])) if k != "nan" else "未填答",
            round(v / sum(list(value_counts.values())) * 100, 2)
        )
        for k, v in sorted(value_counts.items(), key=lambda item: -item[1])
    ])

    plt.figure(dpi=400)
    plt.pie(counts)
    plt.legend(keys, prop=font, loc="best")
    plt.title("「{}」之比例".format(
        column_names[title] if len(column_names[title]) < 20 else "{} ...".format(column_names[title][:20])
    ), fontproperties=font)
    plt.savefig(os.path.join(output_dir, "{}.png".format(title)))
    plt.close()


def main() -> None:

    con = data_preprocessing()
    column_names = column_loader()

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    for sql_path in list([x for x in os.listdir("sql") if x[-4:] == ".sql"]):
        if sql_path == "schema.sql":
            continue

        pd.read_sql_query(
            open(os.path.join("sql", sql_path), "r").read(),
            con=con
        ).rename(
            columns=column_names,
        ).to_excel(
            os.path.join(
                output_dir,
                "{}.xlsx".format(os.path.splitext(sql_path)[0])
            ),
            encoding="utf-8",
            index=False
        )

    for key in column_names:
        if key == "id":
            # Skip first col
            continue

        data = pd.read_sql_query("SELECT {} FROM responds".format(key), con=con).to_numpy().flatten()
        plot_pie_with_raw_data(data, column_names, key, output_dir)


if __name__ == "__main__":
    main()
