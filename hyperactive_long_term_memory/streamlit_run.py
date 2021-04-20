# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


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


def streamlit_table(dataframe):
    st.header("Experiment Statistics")
    st.text("")
    st.table(dataframe.assign(hack="").set_index("hack"))


class DashboardBackend:
    def __init__(self, path):
        self.path = path
        self.ltm_path = self.path + "/ltm_data/"

    def get_expermiment_list(self):
        return os.listdir(self.ltm_path)

    def get_objective_function_list(self, experiment_id):
        return os.listdir(self.ltm_path + experiment_id + "/")

    def read_search_data(self, experiment_id, model_id):
        search_data_path = (
            path + "/ltm_data/" + experiment_id + "/" + model_id + "/search_data.csv"
        )
        return pd.read_csv(search_data_path)

    def read_objective_function(self, experiment_id, model_id):
        objective_function_path = (
            path
            + "/ltm_data/"
            + experiment_id
            + "/"
            + model_id
            + "/objective_function.txt"
        )
        with open(objective_function_path) as f:
            objective_function = f.read()

        return objective_function

    def create_model_statistics(self, model_name_list):
        stats_list = []
        for model_name in model_name_list:
            search_data_path = (
                path
                + "/ltm_data/"
                + exper_select
                + "/"
                + model_name
                + "/search_data.csv"
            )
            search_data = pd.read_csv(search_data_path)
            stats = search_data_statistics(search_data)

            # objective_function = self.read_objective_function(exper_select, model_name)
            # obj_func_name = objective_function.__name__

            stats["Objective Function ID"] = model_name
            # stats["Objective Function"] = obj_func_name
            stats_list.append(stats)

        df = pd.DataFrame(stats_list)
        col_no_obj = list(df.columns)
        col_no_obj.remove("Objective Function ID")
        columns = ["Objective Function ID"] + col_no_obj
        df = df.reindex(columns, axis=1)

        return df


try:
    st.set_page_config(page_title="Long Term Memory Dashboard", layout="wide")
except:
    pass

st.title("Long Term Memory Dashboard")
st.markdown("---")
st.text("")
st.text("")
st.text("")

path = sys.argv[1]

backend = DashboardBackend(path)

st.sidebar.title("Long Term Memory")
st.sidebar.text("")
st.sidebar.text("")
st.sidebar.text("")

exp_name_list = backend.get_expermiment_list()
exper_select = st.sidebar.selectbox("Select Experiment:", exp_name_list)

model_name_list = backend.get_objective_function_list(exper_select)
model_select = st.sidebar.selectbox("Select Objective Function:", model_name_list)


model_statistics = backend.create_model_statistics(model_name_list)
# streamlit_table(model_statistics)


objective_function_str = backend.read_objective_function(exper_select, model_select)


search_data = backend.read_search_data(exper_select, model_select)

col1, col2 = st.beta_columns(2)

col1.header("Experiment Statistics")
col1.text("")
col1.table(model_statistics.assign(hack="").set_index("hack"))

col2.header("Objective Function")
col2.text("")
col2.code(objective_function_str)

st.text("")
st.text("")
st.text("")

st.title("Plots")
st.markdown("---")

st.text("")


from optimization_dashboards import ltm_wrapper

st.sidebar.text("")
st.sidebar.text("")
st.sidebar.text("")

ltm_wrapper.open(search_data)
