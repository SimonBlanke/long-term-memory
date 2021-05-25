# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import os
import dill
import contextlib
import pandas as pd


@contextlib.contextmanager
def atomic_overwrite(filename):
    temp = filename + "~"
    with open(temp, "w") as f:
        yield f
    os.rename(temp, filename)  # this will only happen if no exception was raised


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


class DataIO(Paths):
    def __init__(self, path):
        super().__init__(path)

    def study_list(self):
        return os.listdir(self.ltm_path)

    def model_list(self, exp_id):
        return os.listdir(self.ltm_path + exp_id + "/")

    def read_search_data(self, study_id, model_id):
        search_data_path = (
            self.ltm_path + study_id + "/" + model_id + "/search_data.csv"
        )
        return pd.read_csv(search_data_path)

    def save_search_data(self, search_data, drop_duplicates):
        search_data = self.sd_conv.func2str(search_data)

        search_data_loaded = self._load()
        if not self.replace_existing and search_data_loaded is not None:
            search_data = pd.concat([search_data, search_data_loaded], axis=0)

        if drop_duplicates:
            search_data.drop_duplicates(subset=self.para_names, inplace=True)

        with atomic_overwrite(self.search_data_path) as f:
            search_data.to_csv(f, index=False)

    def read_objective_function(self, study_id, model_id):
        objective_function_path = (
            self.ltm_path + study_id + "/" + model_id + "/objective_function.pkl"
        )
        with open(objective_function_path, "rb") as input_file:
            objective_function = dill.load(input_file)

        return objective_function

    def save_objective_function(self, study_id, model_id):
        with open(
            self.ltm_path
            + "/"
            + study_id
            + "/"
            + model_id
            + "/"
            + "objective_function.pkl",
            "wb",
        ) as output_file:
            dill.dump(self.objective_function, output_file)