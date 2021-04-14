# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import sys
import pathlib
import subprocess
import numpy as np
import pandas as pd
import streamlit as st
from glob import glob
from shutil import copyfile
import plotly.graph_objects as go


try:
    st.set_page_config(page_title="Study Dashboard", layout="wide")
except:
    pass

st.sidebar.title("Study Dashboard")
st.sidebar.text("")
st.sidebar.text("")
st.sidebar.text("")

path = sys.argv[1]


ltm_path = path + "/long_term_memory"

exp_name_list = os.listdir(ltm_path)
exper_select = st.sidebar.selectbox("Select Expermiment", exp_name_list)

model_name_list = os.listdir(path + "/long_term_memory/" + exper_select + "/")
model_select = st.sidebar.selectbox("Select Objective Function", model_name_list)


def search_data_statistics(search_data):
    scores = search_data["score"]

    score_min = scores.min()
    score_avg = scores.mean()
    score_max = scores.max()

    n_samples = len(search_data)

    return {
        "score min": score_min,
        "score mean": score_avg,
        "score max": score_max,
        "n samples": n_samples,
    }


stats_list = []
for model_name in model_name_list:
    search_data_path = (
        path
        + "/long_term_memory/"
        + exper_select
        + "/"
        + model_name
        + "/search_data.csv"
    )
    search_data = pd.read_csv(search_data_path)
    stats = search_data_statistics(search_data)

    stats["Objective Function"] = model_name
    stats_list.append(stats)

df = pd.DataFrame(stats_list)
col_no_obj = list(df.columns)
col_no_obj.remove("Objective Function")
columns = ["Objective Function"] + col_no_obj
df = df.reindex(columns, axis=1)


def plotly_table(df):
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(df.columns), fill_color="paleturquoise", align="left"
                ),
                cells=dict(
                    values=[df[col] for col in df.columns],
                    fill_color="lavender",
                    align="left",
                ),
            )
        ]
    )

    st.plotly_chart(fig)


st.header("Objective Function Statistics")
st.text("")
st.table(df.assign(hack="").set_index("hack"))

# st.dataframe(df)


search_data_path = (
    path + "/long_term_memory/" + exper_select + "/" + model_select + "/search_data.csv"
)
search_data = pd.read_csv(search_data_path)


st.sidebar.text("")
if st.sidebar.button("Start Plot Dashboard"):
    from optimization_dashboards import ltm_wrapper

    st.sidebar.text("")
    st.sidebar.text("")
    st.sidebar.text("")

    ltm_wrapper.open(search_data)

else:
    pass
