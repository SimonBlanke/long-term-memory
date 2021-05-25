# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import glob
import pandas as pd

from .search_data_converter import SearchDataConverter
from .open_dashboard import open_dashboard
from .data_io import DataIO

pd.options.mode.chained_assignment = None


class LTMBackend(DataIO):
    def __init__(self, path):
        super().__init__(path)

    def _init_data_path(self, nth_process):
        # create file name for processes
        if nth_process is not None:
            self.file_name_proc = "search_data_" + str(nth_process) + ".csv"

        search_data_proc_path = self.model_path + self.file_name_proc

        # create csv with header columns if they do not exist
        if not os.path.isfile(search_data_proc_path):
            search_data = pd.DataFrame(columns=self.para_names)
            search_data.to_csv(search_data_proc_path, index=False)

    def _load(self):
        if os.path.isfile(self.search_data_path):
            search_data = pd.read_csv(self.search_data_path)
            search_data = self.sd_conv.str2func(search_data)
            return search_data

    def _append(self, para_dict, drop_duplicates):
        search_data = pd.DataFrame(para_dict, index=[0])
        self.save_search_data(search_data, drop_duplicates)


class LongTermMemory(LTMBackend):
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

    def load(self):
        return self._load()

    def save_on_finish(self, dataframe):
        self.save_search_data(dataframe, self.drop_duplicates)

    def save_on_iteration(self, data_dict, nth_process=None):
        self._init_data_path(nth_process)
        self._append(data_dict, self.drop_duplicates)


class Dashboard:
    def __init__(self, path):
        self.path = path

        # TODO: clean files without dropduplicates for all models

    def open(self):
        open_dashboard(self.path)
