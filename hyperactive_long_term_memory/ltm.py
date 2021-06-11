# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import glob
import dill
from numpy import isin
import pandas as pd

from .search_data_converter import SearchDataConverter
from .open_dashboard import open_dashboard
from .data_io import DataIO, Paths

pd.options.mode.chained_assignment = None


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


class Dashboard:
    def __init__(self, path):
        self.path = path

    def open(self):
        open_dashboard(self.path)
