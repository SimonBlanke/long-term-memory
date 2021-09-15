# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import glob
import dill
from numpy import isin
import pandas as pd
from hyperactive_data_storage import DataCollector


from .search_data_converter import SearchDataConverter
from .open_dashboard import open_dashboard
from .data_io import Paths

pd.options.mode.chained_assignment = None


class LongTermMemory(Paths):
    def __init__(self, path):
        super().__init__(path)
        self.setup_ok_ = False

    def load(self):
        return self.data_c.load()

    def save(self, search_data):
        self.data_c.save(search_data)

    def track(self, objective_function):
        self.objective_function_id = objective_function.__name__

        def wrapper(para):
            results = objective_function(para)

            if isinstance(results, tuple):
                score = results[0]
                results_dict = results[1]
            else:
                score = results
                results_dict = {}

            results_dict["score"] = score

            ltm_data_dict = para.para_dict
            ltm_data_dict.update(results_dict)

            self.data_c.append(ltm_data_dict)

            return results

        wrapper.__name__ = objective_function.__name__

        return wrapper

    def setup(
        self,
        objective_function,
        search_space,
        study_id,
        model_id,
        replace_existing=False,
        drop_duplicates=True,
    ):
        self.setup_ok_ = True

        self.objective_function = objective_function
        self.search_space = search_space

        self.replace_existing = replace_existing
        self.drop_duplicates = drop_duplicates

        self.init_paths(study_id, model_id)

        self.para_names = list(search_space.keys())

        self.data_c = DataCollector(self.search_data_path)
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
