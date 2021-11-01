import streamlit as st
import pandas as pd
import io

import base64
import os
import json
import pickle
import uuid
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import re


def bar_chart(data: np.ndarray, column_names: dict, title: str, output_dir: str) -> None:

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
        v for _, v in sorted(value_counts.items(), key=lambda item: -item[1])
    ])
    keys = list([
        "{} ({}%)".format(
            (k if len(k) < 10 else "{} ...".format(
                k[:10])) if k != "nan" else "未填答",
            round(v / len(data) * 100, 2)
        )
        for k, v in sorted(value_counts.items(), key=lambda item: -item[1])
    ])

    plt.figure(dpi=400)
    plt.pie(counts)
    plt.legend(keys, prop=font, loc="best")
    plt.title("「{}」之比例".format(
        column_names[title] if len(column_names[title]) < 20 else "{} ...".format(
            column_names[title][:20])
    ), fontproperties=font)
    plt.savefig(os.path.join(output_dir, "{}.svg".format(title)))
    plt.close()


def download_button(object_to_download, download_filename, button_text, pickle_it=False):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            #object_to_download = object_to_download.to_csv(index=False)
            towrite = io.BytesIO()
            object_to_download = object_to_download.to_excel(
                towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(towrite.read()).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: .25rem .75rem;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + \
        f'<a download="{download_filename}" id="{button_id}" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">{button_text}</a><br></br>'

    return dl_link


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(encoding='utf_8_sig')
