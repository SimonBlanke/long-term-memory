# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


from tabular_data_explorer.streamlit_elements import create_streamlit_setup


def open_tde(search_data):
    create_streamlit_setup(search_data, plots=None)
