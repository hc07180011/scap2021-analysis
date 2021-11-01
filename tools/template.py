import os
import json
import pandas as pd


def init():

    with open(os.path.join("tools", "columns.json"), "r") as f:
        column_to_id = json.load(f)

    data_dir = os.path.join(".", "data")
    csv_path = list([x for x in os.listdir(data_dir) if "csv" in x])[0]
    return pd.read_csv(os.path.join(data_dir, csv_path), encoding="utf-8")

