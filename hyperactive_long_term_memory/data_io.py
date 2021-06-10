# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import os
import fcntl
import dill
import contextlib
import pandas as pd


@contextlib.contextmanager
def atomic_overwrite(filename):
    # from: https://stackoverflow.com/questions/42409707/pandas-to-csv-overwriting-prevent-data-loss
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


class DataIO:
    def __init__(self, path, drop_duplicates):
        self.path = path
        self.replace_existing = False
        self.drop_duplicates = drop_duplicates

        if self.replace_existing:
            self.mode = "w"
        else:
            self.mode = "a"

    def _get_header(self, search_data, path):
        if os.path.isfile(path):
            if self.replace_existing:
                header = search_data.columns
            else:
                header = False
        else:
            header = search_data.columns
        return header

    def _save_search_data(self, search_data, io_wrap, header):
        if self.drop_duplicates:
            search_data.drop_duplicates(subset=self.drop_duplicates, inplace=True)

        search_data.to_csv(io_wrap, index=False, header=header)

    def atomic_write(self, search_data, path, replace_existing):
        self.replace_existing = replace_existing
        header = self._get_header(search_data, path)

        with atomic_overwrite(path) as io_wrap:
            self._save_search_data(search_data, io_wrap, header)

    def locked_write(self, search_data, path):
        header = self._get_header(search_data, path)

        with open(path, self.mode) as io_wrap:
            fcntl.flock(io_wrap, fcntl.LOCK_EX)
            self._save_search_data(search_data, io_wrap, header)
            fcntl.flock(io_wrap, fcntl.LOCK_UN)

    def load(self, path):
        if os.path.isfile(self.path) and os.path.getsize(self.path) > 0:
            return pd.read_csv(self.path)
