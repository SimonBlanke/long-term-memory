import os
import glob
import numbers
import inspect
import contextlib
import pandas as pd

from .open_dashboard import open_dashboard


@contextlib.contextmanager
def atomic_overwrite(filename):
    temp = filename + "~"
    with open(temp, "w") as f:
        yield f
    os.rename(temp, filename)  # this will only happen if no exception was raised


class DataIO:
    def __init__(self, path=None):
        pass

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

    def _init_data_types(self, search_space):
        self.search_space = search_space
        self.para_names = list(search_space.keys())

        self.search_space_ltm = {}
        self.data_types = {}
        for para_name in search_space.keys():
            value0 = search_space[para_name][0]

            if isinstance(value0, numbers.Number):
                type0 = "number"
                search_dim_ltm = search_space[para_name]

            elif isinstance(value0, str):
                type0 = "string"
                search_dim_ltm = search_space[para_name]

            elif callable(value0):
                type0 = "function"

                search_dim_ltm = []
                for func in list(search_space[para_name]):
                    search_dim_ltm.append(func.__name__)
            else:
                type0 = None
                search_dim_ltm = search_space[para_name]
                print("Warning! data type of ", para_name, " not recognized")
                print("Memory will not work")

            self.data_types[para_name] = type0
            self.search_space_ltm[para_name] = search_dim_ltm

    def _load(self):
        if os.path.isfile(self.ltm_user_path + self.file_name):
            search_data = pd.read_csv(self.ltm_user_path + self.file_name)

            # conv back to func
            for para_name in self.data_types.keys():
                data_type = self.data_types[para_name]

                if data_type != "function":
                    continue

                func_replace = {}
                for func in self.search_space[para_name]:
                    func_name = func.__name__

                    # if not os.path.isfile(self.ltm_user_path + func_name + ".pkl"):
                    #     continue

                    # with open(self.ltm_user_path + func_name + ".pkl", "rb") as file:
                    #     func = pickle.load(file)

                    func_replace[func_name] = func

            search_data[para_name] = search_data[para_name].replace(func_replace)

            return search_data

    def _conv_func(self, search_data, ltm_dir):
        for para_name in self.data_types.keys():
            data_type = self.data_types[para_name]

            if data_type != "function":
                continue

            func_replace = {}
            for func in self.search_space[para_name]:
                func_name = func.__name__

                func_replace[func] = func_name

                # with open(ltm_dir + func_name + ".pkl", "wb") as file:
                #     pickle.dump(func, file)

            search_data[para_name] = search_data[para_name].replace(func_replace)

        return search_data

    def _save(self, search_data, drop_duplicates):
        for ltm_dir in self.ltm_dirs:
            save_para = self.para_names + ["score"]
            search_data = search_data[save_para]

            search_data = self._conv_func(search_data, ltm_dir)

            if drop_duplicates:
                search_data.drop_duplicates(subset=self.para_names, inplace=True)

            with atomic_overwrite(ltm_dir + self.file_name) as f:
                search_data.to_csv(f, index=False)

    def _append(self, para_dict, drop_duplicates):
        for ltm_dir in self.ltm_dirs:
            search_data = pd.read_csv(ltm_dir + self.file_name)
            search_data_new = pd.DataFrame(para_dict, index=[0])
            search_data_new = self._conv_func(search_data_new, ltm_dir)

            search_data = search_data.append(search_data_new)

            if drop_duplicates:
                search_data.drop_duplicates(subset=self.para_names, inplace=True)

            with atomic_overwrite(ltm_dir + self.file_name) as f:
                search_data.to_csv(f, index=False)


class LongTermMemory(DataIO):
    def __init__(
        self,
        path=None,
    ):
        super().__init__(path)
        self.path = path

    def _init_paths(self, model_id, experiment_id):
        self.paths = [self.path]

        self.model_path = "/long_term_memory/" + experiment_id + "/" + model_id + "/"

        self.ltm_dirs = []

        self.file_name = "search_data.csv"

        self.ltm_user_path = self.path + self.model_path

        for path in self.paths:
            self.ltm_dirs.append(path + self.model_path)

    def init_study(
        self,
        objective_function,
        search_space,
        model_id,
        experiment_id="default",
        drop_duplicates=True,
    ):
        self._init_paths(model_id, experiment_id)
        self._init_data_types(search_space)

        # create directories if they do not exist
        for ltm_dir in self.ltm_dirs:
            if not os.path.exists(ltm_dir):
                os.makedirs(ltm_dir, exist_ok=True)

                func_string = inspect.getsource(objective_function)
                with open(ltm_dir + "objective_function.txt", "w") as text_file:
                    text_file.write(func_string)

        self.clean_files(drop_duplicates)

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

    def load(self):
        return self._load()

    def save_on_finish(self, dataframe, drop_duplicates=True):
        self._save(dataframe, drop_duplicates)

    def save_on_iteration(self, data_dict, nth_process, drop_duplicates=True):
        self._init_data_path(nth_process, drop_duplicates)
        self._append(data_dict)

    def open_studyboard(self, path, drop_duplicates=True):
        open_dashboard(path)