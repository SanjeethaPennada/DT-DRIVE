import glob
import json
from itertools import islice
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import seaborn as sns


def batched(iterable, n):
    """Batch data into tuples of length n."""
    it = iter(iterable)
    batch = tuple(islice(it, n))
    while batch:
        yield batch
        batch = tuple(islice(it, n))


DEFAULT_DIR = Path("data/evaluation")
DEFAULT_BENCHMARKING_DIR = DEFAULT_DIR / "benchmarking" / "default"
DEFAULT_RANDOMSEARCH_DIR = DEFAULT_DIR / "random_search"
DEFAULT_RS_VERIFICATION_DIR = DEFAULT_RANDOMSEARCH_DIR / "rs_v3" / "verification"


def _read_file_records(file_path: Path) -> list:
    # extract data from file
    with open(file_path, "r") as f:
        content = json.load(f)

    return content["_checkpoint"]["records"]


def _read_benchmark_file(file_path: Path) -> pd.DataFrame:
    data = {}

    # extract data from path
    parts = file_path.parts
    if len(parts) >= 3:
        rep_id = parts[-3]

        data["rep"] = rep_id[-1]
        path_params = dict(batched(file_path.stem.split("_"), n=2))
        data.update(path_params)
    else:
        print("File path didn't match the pattern")

    data["records"] = _read_file_records(file_path)
    df = pd.DataFrame(data)
    return df


def _calculate_benchmark_dscore_error(df: pd.DataFrame) -> pd.DataFrame:
    oracle_df = df.xs(
        (20, "True"), level=["fps", "highquality"], drop_level=False
    ).sort_index()

    oracle_dscore_vec = oracle_df.groupby("route_index")["driving_score"].mean()
    df["driving_score_error"] = (df["driving_score"] - oracle_dscore_vec).abs()

    return df


def _transform_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index(drop=True)
    # unpack records
    record_df = pd.json_normalize(df["records"])
    # concatenate records data
    df = pd.concat([df, record_df], axis=1)

    # drop original column
    df = df.drop("records", axis=1)

    # remove prefixes from column name
    df.columns = df.columns.str.replace("meta.", "", regex=False)
    df.columns = df.columns.str.replace("scores.", "", regex=False)
    df["driving_score"] = df["score_composed"] / 100
    df = df.rename(columns={"index": "route_index"})

    return df


def load_benchmark_df(
    eval_dir_path: Union[Path, str] = DEFAULT_BENCHMARKING_DIR,
) -> pd.DataFrame:
    eval_dir_path = Path(eval_dir_path)

    if not eval_dir_path.exists():
        raise FileNotFoundError

    file_dfs = []
    for file_path in eval_dir_path.glob("./rep*/**/*.json"):
        file_dfs.append(_read_benchmark_file(file_path))

    df = pd.concat(file_dfs)
    df = _transform_df(df)
    df["fps"] = pd.to_numeric(df["fps"])
    df = df.set_index(["fps", "highquality", "rep", "route_index"])
    df = df.sort_index()

    df = _calculate_benchmark_dscore_error(df)
    return df


def _read_rs_file(file_path: Path):
    data = {}

    # extract data from path
    parts = file_path.parts
    if len(parts) >= 5:
        batch = parts[-3]
        rep = parts[-2]
        it = parts[-1]
        if batch in ("rs_v3", "rs_v4") and "it" in it:
            data["rep"] = int(rep)
            data["it"] = int(it[2:])
            if "4" in batch:
                data["rep"] += 10

            stem_params = dict(batched(file_path.stem.split("_"), n=2))
            data.update(stem_params)
        else:
            return None
    else:
        return None

    # there is only one so take that
    data["records"] = _read_file_records(file_path)[0]
    return data


def load_rs_df(dir_path: Path = DEFAULT_RANDOMSEARCH_DIR) -> pd.DataFrame:
    dir_path = Path(dir_path)

    if not dir_path.exists():
        raise FileNotFoundError

    file_data_list = []
    for file_path in dir_path.glob("./**/*.json"):
        file_data = _read_rs_file(file_path)
        if file_data:
            file_data_list.append(file_data)

    df = pd.DataFrame(file_data_list)
    df = _transform_df(df)
    df = df.set_index(
        [
            "fps",
            "highquality",
            "rep",
            "it",
        ]
    ).sort_index()
    df["route_index"] = df["route_id"].apply(lambda x: int(x.split("_")[-1]))
    return df


def _read_ver_file(file_path: Path) -> pd.DataFrame:
    # DATA FROM PATH
    data = {}
    data["path"] = file_path

    # READ CHECKPOINT
    with open(file_path, "r") as f:
        content = json.load(f)

    data["records"] = content["_checkpoint"]["records"]
    if not data["records"]:
        return

    df = pd.DataFrame(data)
    return _transform_df(df)


def load_ver_df(dir_path: Path = DEFAULT_RS_VERIFICATION_DIR) -> pd.DataFrame:
    dir_path = Path(dir_path)

    if not dir_path.exists():
        raise FileNotFoundError

    dfs = []

    for file_path in dir_path.glob("./**/*.json"):
        dfs.append(_read_ver_file(file_path))

    df = pd.concat(dfs)

    df["route_index"] = df["route_id"].apply(lambda x: int(x.split("_")[-1]))
    df = df.set_index("route_index").sort_index()
    return df


if __name__ == "__main__":
    print("Benchmark df: ")
    print(load_benchmark_df())
    print("Random search df: ")
    print(load_rs_df())
    print("RS Verification df: ")
    print(load_ver_df())
