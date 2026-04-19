import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# from util.load_scenarios import load_scenario_df
from util.load_evaluations import load_benchmark_df

# ------------------------------------------------
# Paths
# ------------------------------------------------

BASE_DIR = Path.cwd().parent

DEFAULT_EVAL_PATH = BASE_DIR / "data" / "evaluation" / "Route_Scenario_36" 

parser = argparse.ArgumentParser()
parser.add_argument(
    "eval_path",
    type=str,
    nargs="?",
    default=None,
    help="Path to evaluation results directory",
)
args = parser.parse_args()

EVAL_PATH = Path(args.eval_path) if args.eval_path else DEFAULT_EVAL_PATH


def main():
    # ------------------------------------------------
    # Load evaluation results
    # ------------------------------------------------

    eval_df = load_benchmark_df(str(EVAL_PATH))

    eval_df = eval_df.add_prefix("eval.")
    df = eval_df.copy()

    # ------------------------------------------------
    # Select infraction columns
    # ------------------------------------------------

    eval_cols = df.columns[df.columns.str.startswith("eval.infractions.")]
    df = df[eval_cols]

    if "eval.infractions.route_dev" in df.columns:
        df = df.drop(columns=["eval.infractions.route_dev"])

    # ------------------------------------------------
    # Prepare dataframe
    # ------------------------------------------------

    df = df.reset_index().set_index(["route_index", "rep"]).sort_index()

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
    # Convert behaviours
    # ------------------------------------------------

    behaviours_df = df.apply(lambda col: col.map(safe_len)).astype(str).agg(" ".join, axis=1)

    # ------------------------------------------------
    # Count unique behaviors per route
    # ------------------------------------------------

    behaviours_count = behaviours_df.groupby("route_index").nunique()
    behaviours_count = behaviours_count.rename("n_behaviors").to_frame()

    # Detect nondeterminism
    behaviours_count["nondeterministic"] = behaviours_count["n_behaviors"] > 1

    # ------------------------------------------------
    # Determinism summary
    # ------------------------------------------------

    deterministic_routes = behaviours_count[~behaviours_count["nondeterministic"]]
    nondeterministic_routes = behaviours_count[behaviours_count["nondeterministic"]]

    print("\nDeterminism summary:")
    print("Deterministic routes:", len(deterministic_routes))
    print("Nondeterministic routes:", len(nondeterministic_routes))

    # ------------------------------------------------
    # Extract route lists
    # ------------------------------------------------

    flaky_routes = nondeterministic_routes.index.tolist()
    stable_routes = deterministic_routes.index.tolist()

    print("\nNondeterministic route IDs:")
    print(flaky_routes)

    print("\nDeterministic route IDs:")
    print(stable_routes)

    # ------------------------------------------------
    # Export to Excel
    # ------------------------------------------------

    pd.DataFrame({"route_index": flaky_routes}).to_excel(
        "nondeterministic_route_ids.xlsx", index=False
    )

    pd.DataFrame({"route_index": stable_routes}).to_excel(
        "deterministic_route_ids.xlsx", index=False
    )

    behaviours_count.reset_index().to_excel("determinism_analysis.xlsx", index=False)

    print("\nExcel files exported:")
    print(" - nondeterministic_route_ids.xlsx")
    print(" - deterministic_route_ids.xlsx")
    print(" - determinism_analysis.xlsx")

    # ------------------------------------------------
    # Create readable determinism column for plotting
    # ------------------------------------------------

    behaviours_count["determinism_type"] = behaviours_count["nondeterministic"].map(
        {False: "Deterministic", True: "Nondeterministic"}
    )

    # ------------------------------------------------
    # Plot determinism distribution
    # ------------------------------------------------

    sns.set_style("whitegrid")

    palette = {"Deterministic": "green", "Nondeterministic": "red"}

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
    plt.title("Determinism Distribution")

    plt.tight_layout()
    plt.savefig("determinism_distribution.png")

    print("\nPlot saved: determinism_distribution.png")

    plt.show()


if __name__ == "__main__":
    main()
