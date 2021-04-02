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
