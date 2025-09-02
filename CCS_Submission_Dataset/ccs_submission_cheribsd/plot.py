#!/usr/bin/env python3
import os
import re
import sys
import argparse
import statistics
import math
import matplotlib.pyplot as plt

def group_files_by_algo_and_time(directory):
    """
    Groups log files in the given directory by time marker and algorithm.
    Expected filename format: "<algorithm>_<time>.txt"
    For example, "find_max_12.txt" -> algorithm: "find_max", time: "12".
    Returns a dictionary: groups[time][algorithm] = list_of_file_paths.
    """
    groups = {}
    for filename in os.listdir(directory):
        if not filename.lower().endswith(".txt"):
            continue
        m = re.search(r"(.*?)_(\d+)\.txt$", filename, re.IGNORECASE)
        if m:
            algo = m.group(1)
            time_group = m.group(2)
            groups.setdefault(time_group, {}).setdefault(algo, []).append(os.path.join(directory, filename))
    return groups

def compute_combined_stats_from_files(file_list):
    """
    Reads log files from file_list and extracts combined CPU times (user + sys).
    Each log line is expected to be of the form:
      1.05 real         0.77 user         0.22 sys
    This function sums the user and sys times, then computes the overall mean 
    and sample standard deviation over all such lines.
    Returns a tuple (mean, std) or None if no data is found.
    """
    combined_values = []
    pattern = re.compile(r"(\d+\.\d+)\s+real\s+(\d+\.\d+)\s+user\s+(\d+\.\d+)\s+sys")
    for filepath in file_list:
        try:
            with open(filepath, "r") as f:
                for line in f:
                    match = pattern.search(line)
                    if match:
                        # Sum user and sys times.
                        user_time = float(match.group(2))
                        sys_time  = float(match.group(3))
                        combined_values.append(user_time + sys_time)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    if not combined_values:
        return None
    try:
        mean_val = statistics.mean(combined_values)
        std_val  = statistics.stdev(combined_values) if len(combined_values) > 1 else 0.0
        return mean_val, std_val
    except Exception as e:
        print(f"Statistics error: {e}")
        return None

def compute_overhead_ratio(stats1, stats2):
    """
    Given statistics (mean, std) for directory 1 and directory 2, 
    compute the overhead ratio as mean1 / mean2.
    Propagates the error assuming independent uncertainties:
      relative_error = sqrt((std1/mean1)^2 + (std2/mean2)^2)
      error = ratio * relative_error.
    Returns a tuple (ratio, error) or None if division by zero occurs.
    """
    mean1, std1 = stats1
    mean2, std2 = stats2
    if mean2 == 0:
        return None
    ratio = mean1 / mean2
    rel_err1 = (std1/mean1) if mean1 != 0 else 0
    rel_err2 = (std2/mean2) if mean2 != 0 else 0
    rel_error = math.sqrt(rel_err1**2 + rel_err2**2)
    error = ratio * rel_error
    return ratio, error

def main():
    parser = argparse.ArgumentParser(
        description="Compute overhead ratios for log files grouped by time and algorithm.\n"
                    "Expected filename format: <algorithm>_<time>.txt (e.g., find_max_12.txt, binary_search_12.txt).\n"
                    "For each common time group and algorithm present in both directories, the ratio = (Dir1 mean) / (Dir2 mean) is computed."
    )
    parser.add_argument("dir1", help="Path to the first directory.")
    parser.add_argument("dir2", help="Path to the second directory.")
    parser.add_argument("--save", 
                        help="Output file path for saving the figure (default: overhead_comparison.png)",
                        default="overhead_comparison.png")
    args = parser.parse_args()

    # Validate input directories.
    if not os.path.isdir(args.dir1):
        print(f"Error: {args.dir1} is not a valid directory.")
        sys.exit(1)
    if not os.path.isdir(args.dir2):
        print(f"Error: {args.dir2} is not a valid directory.")
        sys.exit(1)

    # Group files by time marker and algorithm.
    groups_dir1 = group_files_by_algo_and_time(args.dir1)
    groups_dir2 = group_files_by_algo_and_time(args.dir2)

    # Determine common time groups.
    common_time_groups = set(groups_dir1.keys()).intersection(groups_dir2.keys())
    if not common_time_groups:
        print("No common time groups found between the two directories.")
        sys.exit(0)

    # Build a nested dictionary for overhead data:
    # overhead_data[time_group][algorithm] = (ratio, error)
    overhead_data = {}
    for time_group in common_time_groups:
        algos_dir1 = set(groups_dir1[time_group].keys())
        algos_dir2 = set(groups_dir2[time_group].keys())
        common_algos = algos_dir1.intersection(algos_dir2)
        if not common_algos:
            continue
        overhead_data[time_group] = {}
        for algo in common_algos:
            stats1 = compute_combined_stats_from_files(groups_dir1[time_group][algo])
            stats2 = compute_combined_stats_from_files(groups_dir2[time_group][algo])
            if stats1 is None or stats2 is None:
                continue
            ratio_result = compute_overhead_ratio(stats1, stats2)
            if ratio_result is None:
                continue
            overhead_data[time_group][algo] = ratio_result

    # Remove any time groups without valid algorithm data.
    overhead_data = {tg: data for tg, data in overhead_data.items() if data}
    if not overhead_data:
        print("No valid overhead data to plot.")
        sys.exit(0)

    # --- Plotting ---
    # Fixed color mapping for known algorithms.
    ALGORITHM_COLORS = {
        "find_max": "orange",
        "binary_search": "blue",
        "matrix_mult": "red",
        "intsort": "green"
    }

    # Sort time groups numerically.
    sorted_time_groups = sorted(overhead_data.keys(), key=lambda x: int(x))
    n_groups = len(sorted_time_groups)
    
    # For each time group, get the sorted list of algorithms.
    group_algos = {tg: sorted(overhead_data[tg].keys()) for tg in sorted_time_groups}
    
    # Determine bar width: allocate a total width (e.g. 0.8) per time group.
    max_algos = max(len(algos) for algos in group_algos.values())
    total_width = 0.8  
    bar_width = total_width / max_algos
    
    fig, ax = plt.subplots()
    x_positions = list(range(n_groups))
    
    # Track algorithm labels to add only once to the legend.
    algo_labels_plotted = {}
    
    # For each time group, plot a bar per algorithm.
    for i, time_group in enumerate(sorted_time_groups):
        algos = group_algos[time_group]
        n_algos = len(algos)
        # Center the bars for this group.
        start_offset = - (n_algos - 1) * bar_width / 2
        for j, algo in enumerate(algos):
            x = i + start_offset + j * bar_width
            ratio, error = overhead_data[time_group][algo]
            # Use the fixed color for the algorithm.
            chosen_color = ALGORITHM_COLORS.get(algo, "gray")
            label = algo if algo not in algo_labels_plotted else None
            if label is not None:
                algo_labels_plotted[algo] = True
            ax.bar(x, ratio, bar_width, yerr=error, capsize=4, label=label, color=chosen_color)
            # Annotate the bar with the ratio value.
            ax.text(x, ratio, f"{ratio:.2f}", ha='center', va='bottom', fontsize=8)
    
    ax.set_xticks(x_positions)
    ax.set_xticklabels(sorted_time_groups)
    ax.set_xlabel("Time Group")
    ax.set_ylabel("Overhead Ratio (Dir1 / Dir2)")
    ax.set_title("Overhead Ratio by Time Group and Algorithm")
    ax.legend(title="Algorithm")
    plt.tight_layout()
    plt.savefig(args.save)
    print(f"Figure saved as {args.save}")
    plt.show()

if __name__ == "__main__":
    main()
