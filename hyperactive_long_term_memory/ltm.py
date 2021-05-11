# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import dill
import glob
import contextlib
import pandas as pd

from .search_data_converter import SearchDataConverter
from .open_dashboard import open_dashboard

pd.options.mode.chained_assignment = None


@contextlib.contextmanager
def atomic_overwrite(filename):
    temp = filename + "~"
    with open(temp, "w") as f:
        yield f
    os.rename(temp, filename)  # this will only happen if no exception was raised


class LongTermMemory:
    def __init__(
        self,
        path=None,
    ):
        self.path = path

    def _init_paths(self, model_id, study_id):
        self.paths = [self.path]
        self.ltm_path = self.path + "/ltm_data/"

        self.model_path = "/ltm_data/" + study_id + "/" + model_id + "/"

        self.ltm_dirs = []

        self.file_name = "search_data.csv"

        self.ltm_user_path = self.path + self.model_path

        for path in self.paths:
            self.ltm_dirs.append(path + self.model_path)

    def _init_data_path(self, nth_process):
        process_paths = []
        # create file name for processes
        if nth_process is not None:
            self.file_name = "search_data_" + str(nth_process) + ".csv"

            for path in self.paths:
                process_paths.append(path + self.model_path + self.file_name)

        # create csv with header columns if they do not exist
        for process_path in process_paths:
            if not os.path.isfile(process_path):
                search_data = pd.DataFrame(columns=self.para_names)
                search_data.to_csv(process_path, index=False)

    def _load(self):
        if os.path.isfile(self.ltm_user_path + self.file_name):
            search_data = pd.read_csv(self.ltm_user_path + self.file_name)
            search_data = self.sd_conv.str2func(search_data)

            return search_data

    def _save(self, search_data, drop_duplicates):
        for ltm_dir in self.ltm_dirs:
            search_data = self.sd_conv.func2str(search_data)

            search_data_loaded = self._load()
            if not self.replace_existing and search_data_loaded is not None:
                search_data = pd.concat([search_data, search_data_loaded], axis=0)

            if drop_duplicates:
                search_data.drop_duplicates(subset=self.para_names, inplace=True)

            with atomic_overwrite(ltm_dir + self.file_name) as f:
                search_data.to_csv(f, index=False)

    def _append(self, para_dict, drop_duplicates):
        for ltm_dir in self.ltm_dirs:
            search_data = pd.DataFrame(para_dict, index=[0])
            search_data = self.sd_conv.func2str(search_data)

            if not self.replace_existing and self.search_data_loaded is not None:
                search_data_loaded = self._load()
                search_data = pd.concat([search_data, search_data_loaded], axis=0)

            if drop_duplicates:
                search_data.drop_duplicates(subset=self.para_names, inplace=True)

            with atomic_overwrite(ltm_dir + self.file_name) as f:
                search_data.to_csv(f, index=False)

    def clean_files(self, drop_duplicates):
        for ltm_dir in self.ltm_dirs:
            search_data_proc_paths = glob.glob(ltm_dir + "search_data_*.csv")
            search_data_paths = glob.glob(ltm_dir + "search_data*.csv")

            search_data_list = []
            for search_data_path in search_data_paths:
                search_data_ = pd.read_csv(search_data_path)
                search_data_list.append(search_data_)

            if len(search_data_list) > 0:
                search_data = pd.concat(search_data_list, axis=0)
                search_data.to_csv(ltm_dir + "search_data.csv", index=False)

                if drop_duplicates:
                    search_data.drop_duplicates(subset=self.para_names, inplace=True)

            # remove search_data_* files
            for search_data_proc_path in search_data_proc_paths:
                if os.path.exists(search_data_proc_path):
                    os.remove(search_data_proc_path)

    def init_experiment(
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

        self._init_paths(model_id, study_id)
        self.para_names = list(search_space.keys())

        self.sd_conv = SearchDataConverter(search_space)

        # create directories if they do not exist
        for ltm_dir in self.ltm_dirs:
            if not os.path.exists(ltm_dir):
                os.makedirs(ltm_dir, exist_ok=True)

            if not os.path.exists(ltm_dir + "objective_function.pkl"):
                """
                func_string = inspect.getsource(objective_function)
                with open(ltm_dir + "objective_function.txt", "w") as text_file:
                    text_file.write(func_string)
                """
                with open(ltm_dir + "objective_function.pkl", "wb") as output_file:
                    dill.dump(self.objective_function, output_file)

        self.clean_files(drop_duplicates)

    def load(self):
        return self._load()

    def save_on_finish(self, dataframe, drop_duplicates=True):
        self._save(dataframe, drop_duplicates)

    def save_on_iteration(self, data_dict, nth_process=None, drop_duplicates=True):
        self._init_data_path(nth_process)
        self._append(data_dict, drop_duplicates)


class Dashboard:
    def __init__(self, path):
        self.path = path

    def open(self):
        open_dashboard(self.path)
