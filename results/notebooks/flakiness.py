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

DEFAULT_EVAL_PATH = BASE_DIR / "data" / "evaluation" / "default_flaky"


# ------------------------------------------------
# Argument parser
# ------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument(
    "--eval_path",
    type=str,
    default=None,
    help="Path to evaluation results"
)

args = parser.parse_args()

EVAL_PATH = Path(args.eval_path) if args.eval_path else DEFAULT_EVAL_PATH


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
# Flakiness analysis
# ------------------------------------------------

def analyze_flakiness(eval_path):

    print("\n====================================")
    print("Flakiness Analysis")
    print("====================================")

    eval_df = load_benchmark_df(str(eval_path))

    eval_df = eval_df.add_prefix("eval.")
    df = eval_df.copy()

    # Select infraction columns
    eval_cols = df.columns[df.columns.str.startswith("eval.infractions.")]
    df = df[eval_cols]

    # Remove unwanted column
    if "eval.infractions.route_dev" in df.columns:
        df = df.drop(columns=["eval.infractions.route_dev"])

    # Prepare dataframe
    df = df.reset_index().set_index(["route_index", "rep"]).sort_index()

    # Convert behaviour values
    behaviours_df = df.apply(lambda col: col.map(safe_len)).astype(str).agg(" ".join, axis=1)

    # Count unique behaviours per route
    behaviours_count = behaviours_df.groupby("route_index").nunique()

    behaviours_count = behaviours_count.rename("n_behaviors").to_frame()

    behaviours_count["nondeterministic"] = behaviours_count["n_behaviors"] > 1

    print("\nFlakiness distribution:")
    print(behaviours_count["n_behaviors"].value_counts())

    # --------------------------------
    # Extract route lists
    # --------------------------------

    flaky_routes = behaviours_count[behaviours_count["nondeterministic"]].index.tolist()
    deterministic_routes = behaviours_count[~behaviours_count["nondeterministic"]].index.tolist()

    print("\nFlaky route IDs:")
    print(flaky_routes)

    print("\nDeterministic route IDs:")
    print(deterministic_routes)

    # --------------------------------
    # Export to Excel
    # --------------------------------

    pd.DataFrame({"route_index": flaky_routes}).to_excel(
        "flaky_route_ids.xlsx", index=False
    )

    pd.DataFrame({"route_index": deterministic_routes}).to_excel(
        "deterministic_route_ids.xlsx", index=False
    )

    behaviours_count.reset_index().to_excel(
        "route_flakiness_analysis.xlsx", index=False
    )

    print("\nExcel files exported:")
    print(" - flaky_route_ids.xlsx")
    print(" - deterministic_route_ids.xlsx")
    print(" - route_flakiness_analysis.xlsx")

    # --------------------------------
    # Plot flakiness distribution
    # --------------------------------

    sns.set_style("whitegrid")

    palette = {False: "green", True: "red"}

    plt.figure()

    sns.histplot(
        data=behaviours_count,
        x="n_behaviors",
        hue="nondeterministic",
        stat="percent",
        discrete=True,
        palette=palette
    )

    plt.xlabel("Number of Behaviors")
    plt.ylabel("Percentage of Routes")
    plt.title("Flakiness Distribution")

    plt.tight_layout()

    plt.savefig("flakiness_distribution.png")

    print("\nPlot saved: flakiness_distribution.png")

    plt.show()


# ------------------------------------------------
# Main
# ------------------------------------------------

def main():

    analyze_flakiness(EVAL_PATH)


if __name__ == "__main__":
    main()
