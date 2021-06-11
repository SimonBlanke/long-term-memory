# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import os
import dill
import pandas as pd


class Paths:
    def __init__(self, path):
        self.path = path
        self.ltm_path = self.path + "/ltm_data/"

    def init_paths(self, study_id, model_id):
        self.ltm_path = self.path + "/ltm_data/"
        self.model_path_ = "/" + study_id + "/" + model_id + "/"
        self.file_name_ = "search_data.csv"

        self.model_path = self.ltm_path + self.model_path_
        self.search_data_path = self.ltm_path + self.model_path_ + self.file_name_

        # create directories if they do not exist
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path, exist_ok=True)
        elif not os.path.exists(self.ltm_path):
            os.makedirs(self.ltm_path, exist_ok=True)

    def read_objective_function(self, study_id, model_id):
        objective_function_path = (
            self.ltm_path + study_id + "/" + model_id + "/objective_function.pkl"
        )
        with open(objective_function_path, "rb") as input_file:
            objective_function = dill.load(input_file)

        return objective_function

    def study_list(self):
        return os.listdir(self.ltm_path)

    def model_list(self, exp_id):
        return os.listdir(self.ltm_path + exp_id + "/")

    def read_search_data(self, study_id, model_id):
        self.ltm_path = self.path + "/ltm_data/"
        self.model_path_ = "/" + study_id + "/" + model_id + "/"
        self.file_name_ = "search_data.csv"

        self.model_path = self.ltm_path + self.model_path_
        self.search_data_path = self.ltm_path + self.model_path_ + self.file_name_

        return pd.read_csv(self.search_data_path)
