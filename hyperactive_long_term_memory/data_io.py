import os
import pandas as pd


class DataIO:
    def __init__(self, path=None):
        pass

    def studys(self):
        return os.listdir(self.ltm_path)

    def objective_functions(self, study_id):
        return os.listdir(self.ltm_path + study_id + "/")

    def search_data(self, study_id, model_id):
        search_data_path = (
            self.ltm_path + study_id + "/" + model_id + "/search_data.csv"
        )
        return pd.read_csv(search_data_path)
