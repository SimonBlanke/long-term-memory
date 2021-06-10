# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import sys

import inspect
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from tde_wrapper import open_tde
from data_io import Paths


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


def streamlit_table(dataframe, _st_):
    _st_.header("Experiment Statistics")
    _st_.text("")
    _st_.table(dataframe.assign(hack="").set_index("hack"))


class DashboardBackend(Paths):
    def __init__(self, path):
        super().__init__(path)

    def create_model_statistics(self, study_id, model_name_list):
        stats_list = []
        for model_id in model_list:
            search_data = self.read_search_data(study_id, model_id)
            stats = search_data_statistics(search_data)

            objective_function = self.read_objective_function(study_id, model_id)
            obj_func_name = objective_function.__name__

            stats["Model ID"] = model_id
            stats["Objective Function"] = obj_func_name
            stats_list.append(stats)

        df = pd.DataFrame(stats_list)
        col_no_obj = list(df.columns)
        col_no_obj.remove("Model ID")
        col_no_obj.remove("Objective Function")

        columns = ["Model ID", "Objective Function"] + col_no_obj

        df = df.reindex(columns, axis=1)

        return df


try:
    st.set_page_config(page_title="Long Term Memory Dashboard", layout="wide")
except:
    pass


path = sys.argv[1]

backend = DashboardBackend(path)

st.sidebar.title("Long Term Memory")
st.sidebar.text("")
st.sidebar.text("")
st.sidebar.text("")

study_list = backend.study_list()
study_select = st.sidebar.selectbox("Select Study:", study_list)

model_list = backend.model_list(study_select)
model_select = st.sidebar.selectbox("Select Model:", model_list)

model_statistics = backend.create_model_statistics(study_select, model_list)

st.header(study_select + " Study Statistics")
st.text("")
st.table(model_statistics.assign(hack="").set_index("hack"))

st.markdown("---")
st.text("")
st.text("")
st.text("")


objective_function = backend.read_objective_function(study_select, model_select)
objective_function_str = inspect.getsource(objective_function)


search_data = backend.read_search_data(study_select, model_select)
col1, col2 = st.beta_columns(2)

st.header(model_select)


col1.header("Objective Function")
col1.text("")
col1.code(objective_function_str)

# plotly_table(search_data, col2)
# streamlit_table(search_data, col2)


# Tabular Data Explorer

st.sidebar.text("")
st.sidebar.text("")
st.sidebar.text("")

open_tde(search_data)
