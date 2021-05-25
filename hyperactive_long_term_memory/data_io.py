# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import os
import dill
import pandas as pd


class DataIO:
    def __init__(self, path):
        self.path = path
        self.ltm_path = self.path + "/ltm_data/"

    def expermiments(self):
        return os.listdir(self.ltm_path)

    def objective_functions(self, study_id):
        return os.listdir(self.ltm_path + study_id + "/")

    def search_data(self, study_id, model_id):
        search_data_path = (
            self.ltm_path + study_id + "/" + model_id + "/search_data.csv"
        )
        return pd.read_csv(search_data_path)

    def objective_function(self, experiment_id, model_id):
        objective_function_path = (
            self.ltm_path + experiment_id + "/" + model_id + "/objective_function.pkl"
        )
        with open(objective_function_path, "rb") as input_file:
            objective_function = dill.load(input_file)

        return objective_function
