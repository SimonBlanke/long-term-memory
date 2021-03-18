# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import os
import sys
import json
import dill
import shutil
import inspect
import hashlib
import datetime
import glob


def function_string(function):
    return inspect.getsource(function)


def object_hash(object):
    return hashlib.sha1(object).hexdigest()


def model_id(model):
    return str(object_hash(function_string(model).encode("utf-8")))


def get_datetime():
    return datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S:%f")


def is_sha1(maybe_sha):
    if (
        not isinstance(maybe_sha, int)
        and not isinstance(maybe_sha, float)
        and not isinstance(maybe_sha, str)
    ):
        if len(maybe_sha) == 40:
            return True

    return False


def _get_pkl_hash(hash, model_path):
    paths = glob.glob(model_path + hash + "*.pkl")

    return paths


def _hash2obj(search_space, model_path):
    hash2obj_dict = {}
    para_hash_list = _get_para_hash_list(search_space)

    for para_hash in para_hash_list:
        obj = _read_dill(para_hash, model_path)
        hash2obj_dict[para_hash] = obj

    return hash2obj_dict


def _read_dill(value, model_path):
    paths = _get_pkl_hash(value, model_path)
    assert len(paths) != 0

    for path in paths:
        with open(path, "rb") as fp:
            value = dill.load(fp)
            value = dill.loads(value)
            break

    return value


def _get_para_hash_list(search_space):
    para_hash_list = []
    for key in search_space.keys():
        values = search_space[key]

        for value in values:
            if (
                not isinstance(value, int)
                and not isinstance(value, float)
                and not isinstance(value, str)
            ):

                para_dill = dill.dumps(value)
                para_hash = object_hash(para_dill)
                para_hash_list.append(para_hash)

    return para_hash_list


def _connect_key2value(data, key_model, value_model):
    if value_model in data[key_model]:
        print("IDs of models are already connected")
    else:
        data[key_model].append(value_model)
        print("IDs successfully connected")

    return data


def _split_key_value(data, key_model, value_model):
    if value_model in data[key_model]:
        data[key_model].remove(value_model)

        if len(data[key_model]) == 0:
            del data[key_model]
        print("ID connection successfully deleted")
    else:
        print("IDs of models are not connected")

    return data


def _reset_memory(meta_path):
    dirs = next(os.walk(meta_path))[1]
    for dir in dirs:
        shutil.rmtree(meta_path + dir)

    with open(meta_path + "model_connections.json", "w") as f:
        json.dump({}, f, indent=4)

    print("Memory reset successful")


def _query_yes_no():
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    question = "Delete the entire long term memory?"

    while True:
        sys.stdout.write(question + " [y/n] ")
        choice = input().lower()
        if choice == "":
            return False
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")
