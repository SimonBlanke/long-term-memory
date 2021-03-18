# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


from .utils import object_hash


def model_path(model_id):
    return "model_id:" + model_id + "/"


def date_path(datetime):
    return "run_data/" + datetime + "/"


def meta_data_name(X, y):
    return "dataset_id:" + object_hash(X) + "_" + object_hash(y) + "_.csv"
