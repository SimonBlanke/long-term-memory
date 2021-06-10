# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import glob
from numpy import isin
import pandas as pd

from .search_data_converter import SearchDataConverter
from .open_dashboard import open_dashboard
from .data_io import DataIO, Paths

pd.options.mode.chained_assignment = None


class DataCollector:
    def __init__(self, path, drop_duplicates=False):
        self.path = path
        self.drop_duplicates = drop_duplicates

        self.path2file = path.rsplit("/", 1)[0] + "/"
        self.file_name = path.rsplit("/", 1)[1]

        self.io = DataIO(path, drop_duplicates)

    def load(self):
        return self.io.load(self.path)

    def save_iter(self, dictionary):
        search_data = pd.DataFrame(dictionary, index=[0])
        self.io.locked_write(search_data, self.path)

    def save_run(self, dataframe, replace_existing=False):
        self.io.atomic_write(dataframe, self.path, replace_existing)


class LongTermMemory(Paths):
    def __init__(self, path):
        super().__init__(path)

    def init_study(
        self,
        objective_function,
        search_space,
        study_id,
        model_id,
        replace_existing=False,
        drop_duplicates=True,
    ):
        self.objective_function = objective_function
        self.search_space = search_space

        self.replace_existing = replace_existing
        self.drop_duplicates = drop_duplicates

        self.init_paths(study_id, model_id)

        self.para_names = list(search_space.keys())

        self.sd_conv = SearchDataConverter(search_space)

        if not os.path.exists(self.model_path + "objective_function.pkl"):
            self.save_objective_function(study_id, model_id)

        self.clean_files(drop_duplicates)

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

    def clean_files(self, drop_duplicates):
        search_data_proc_paths = glob.glob(
            self.ltm_path + self.model_path + "search_data_*.csv"
        )
        search_data_paths = glob.glob(
            self.ltm_path + self.model_path + "search_data*.csv"
        )

        search_data_list = []
        for search_data_path in search_data_paths:
            search_data_ = pd.read_csv(search_data_path)
            search_data_list.append(search_data_)

        if len(search_data_list) > 0:
            search_data = pd.concat(search_data_list, axis=0)
            search_data.to_csv(self.search_data_path, index=False)

            if drop_duplicates:
                search_data.drop_duplicates(subset=self.para_names, inplace=True)

        # remove search_data_* files
        for search_data_proc_path in search_data_proc_paths:
            if os.path.exists(search_data_proc_path):
                os.remove(search_data_proc_path)


class Dashboard:
    def __init__(self, path):
        self.path = path

        # TODO: clean files without dropduplicates for all models

    def open(self):
        open_dashboard(self.path)
