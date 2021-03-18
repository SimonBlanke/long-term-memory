import os
import glob
import contextlib
import pandas as pd


@contextlib.contextmanager
def atomic_overwrite(filename):
    temp = filename + "~"
    with open(temp, "w") as f:
        yield f
    os.rename(temp, filename)  # this will only happen if no exception was raised


class DataIO:
    def __init__(self, path=None, save_on="finish"):
        pass

    def clean_files(self):
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

            # remove search_data_* files
            for search_data_proc_path in search_data_proc_paths:
                if os.path.exists(search_data_proc_path):
                    os.remove(search_data_proc_path)

    def _init_data_path(self, search_space, nth_process):
        self.para_names = list(search_space.keys())

        # create file name for processes
        if nth_process is not None:
            self.file_name = "search_data_" + str(nth_process) + ".csv"

            for path in self.paths:
                self.ltm_paths.append(path + self.model_path + self.file_name)

        # create directories if they do not exist
        for ltm_dir in self.ltm_dirs:
            if not os.path.exists(ltm_dir):
                os.makedirs(ltm_dir)

        # create csv with header columns if they do not exist
        for ltm_path in self.ltm_paths:
            if not os.path.isfile(ltm_path):
                search_data = pd.DataFrame(columns=self.para_names)
                search_data.to_csv(ltm_path, index=False)

    def _load(self):
        if os.path.isfile(self.ltm_user_path):
            return pd.read_csv(self.ltm_user_path)

    def _save(self, search_data):
        for ltm_path in self.ltm_paths:
            save_para = self.para_names + ["score"]
            search_data = search_data[save_para]

            with atomic_overwrite(ltm_path) as f:
                search_data.to_csv(f, index=False)

    def _append(self, para_dict):
        for ltm_path in self.ltm_paths:
            search_data = pd.read_csv(ltm_path)
            search_data_new = pd.DataFrame(para_dict, index=[0])
            search_data = search_data.append(search_data_new)

            with atomic_overwrite(ltm_path) as f:
                search_data.to_csv(f, index=False)


class LongTermMemory(DataIO):
    def __init__(
        self,
        model_id,
        experiment_id="default",
        path=None,
        save_on="finish",
        backup=False,
    ):
        super().__init__(path, save_on)
        self.save_on = save_on

        self.paths = [path]

        if backup:
            default_path, _ = os.path.realpath(__file__).rsplit("/", 1)
            default_path = default_path + "/"
            self.paths.append(default_path)

        self.model_path = "/long_term_memory/" + experiment_id + "/" + model_id + "/"

        self.ltm_paths = []
        self.ltm_dirs = []

        self.file_name = "search_data.csv"

        self.ltm_user_path = path + self.model_path + self.file_name

        for path in self.paths:
            self.ltm_dirs.append(path + self.model_path)
