import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from util.load_evaluations import load_benchmark_df


# ------------------------------------------------
# Paths
# ------------------------------------------------

BASE_DIR = Path.cwd().parent


DEFAULT_EVAL_PATH_1 = BASE_DIR / "data" / "evaluation" / "dt_drive_TransFuser++" / "Route_Scenario_36"
DEFAULT_EVAL_PATH_2 = BASE_DIR / "data" / "evaluation" / "dt_drive_TransFuser" / "Route_Scenario_36"


parser = argparse.ArgumentParser()

parser.add_argument("--eval_path_1", type=str, default=None,
                    help="Path to first ADS evaluation results")

parser.add_argument("--eval_path_2", type=str, default=None,
                    help="Path to second ADS evaluation results")

args = parser.parse_args()

EVAL_PATH_1 = Path(args.eval_path_1) if args.eval_path_1 else DEFAULT_EVAL_PATH_1
EVAL_PATH_2 = Path(args.eval_path_2) if args.eval_path_2 else DEFAULT_EVAL_PATH_2


# ------------------------------------------------
# Safe length function
# ------------------------------------------------

def safe_len(x):

    if isinstance(x, (list, tuple, set)):
        return len(x)

    if pd.isna(x):
        return 0

    if isinstance(x, bool):
        return int(x)

    if isinstance(x, (int, float)):
        return int(x)

    if isinstance(x, str):

        if x.lower() == "true":
            return 1

        if x.lower() == "false":
            return 0

        try:
            return int(x)

        except:
            return 0

    return 0


# ------------------------------------------------
# Determinism analysis + plotting
# ------------------------------------------------

def analyze_ads(eval_path, ads_name):

    print(f"\n==============================")
    print(f"Analyzing {ads_name}")
    print(f"==============================")

    eval_df = load_benchmark_df(str(eval_path))

    eval_df = eval_df.add_prefix("eval.")
    df = eval_df.copy()

    # Select infraction columns
    eval_cols = df.columns[df.columns.str.startswith("eval.infractions.")]
    df = df[eval_cols]

    if "eval.infractions.route_dev" in df.columns:
        df = df.drop(columns=["eval.infractions.route_dev"])

    # Prepare dataframe
    df = df.reset_index().set_index(["route_index", "rep"]).sort_index()

    # Convert behaviours
    behaviours_df = df.apply(lambda col: col.map(safe_len)).astype(str).agg(" ".join, axis=1)

    # Count unique behaviors per route
    behaviours_count = behaviours_df.groupby("route_index").nunique()
    behaviours_count = behaviours_count.rename("n_behaviors").to_frame()

    behaviours_count["nondeterministic"] = behaviours_count["n_behaviors"] > 1

    # Summary
    deterministic_routes = behaviours_count[~behaviours_count["nondeterministic"]]
    nondeterministic_routes = behaviours_count[behaviours_count["nondeterministic"]]

    print("Deterministic routes:", len(deterministic_routes))
    print("Nondeterministic routes:", len(nondeterministic_routes))

    flaky_routes = nondeterministic_routes.index.tolist()
    stable_routes = deterministic_routes.index.tolist()

    # Export Excel
    pd.DataFrame({"route_index": flaky_routes}).to_excel(
        f"{ads_name}_nondeterministic_routes.xlsx", index=False
    )

    pd.DataFrame({"route_index": stable_routes}).to_excel(
        f"{ads_name}_deterministic_routes.xlsx", index=False
    )

    behaviours_count.reset_index().to_excel(
        f"{ads_name}_determinism_analysis.xlsx", index=False
    )

    print(f"\nExcel files exported for {ads_name}")

    # ------------------------------------------------
    # Plot determinism distribution (same style as original)
    # ------------------------------------------------

    behaviours_count["determinism_type"] = behaviours_count["nondeterministic"].map(
        {False: "Deterministic", True: "Nondeterministic"}
    )

    sns.set_style("whitegrid")

    palette = {"Deterministic": "green", "Nondeterministic": "red"}

    plt.figure()

    sns.histplot(
        data=behaviours_count,
        x="determinism_type",
        hue="determinism_type",
        stat="percent",
        discrete=True,
        palette=palette,
    )

    plt.xlabel("Route Type")
    plt.ylabel("Percentage of Routes")
    plt.title(f"Determinism Distribution ({ads_name})")

    plt.tight_layout()

    plot_name = f"{ads_name}_determinism_distribution.png"
    plt.savefig(plot_name)

    print(f"Plot saved: {plot_name}")

    plt.show()


# ------------------------------------------------
# Main
# ------------------------------------------------

def main():

    analyze_ads(EVAL_PATH_1, "TransFuser++")
    analyze_ads(EVAL_PATH_2, "TransFuser")


if __name__ == "__main__":
    main()
