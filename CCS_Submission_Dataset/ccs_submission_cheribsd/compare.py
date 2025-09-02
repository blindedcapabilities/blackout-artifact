#!/usr/bin/env python3
import os
import re
import sys
import statistics
import argparse

def compute_stats(filepath):
    """
    Processes a single file to extract timing information and computes statistics.
    
    Returns a dictionary with computed stats or None if no valid data is found.
    """
    real_times = []
    user_times = []
    sys_times = []
    
    # Pattern to match lines such as:
    # "1.05 real         0.77 user         0.22 sys"
    pattern = re.compile(r"(\d+\.\d+)\s+real\s+(\d+\.\d+)\s+user\s+(\d+\.\d+)\s+sys")
    
    try:
        with open(filepath, "r") as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    real_times.append(float(match.group(1)))
                    user_times.append(float(match.group(2)))
                    sys_times.append(float(match.group(3)))
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None
    
    if not real_times:
        return None

    stats = {}
    stats["real_mean"] = statistics.mean(real_times)
    stats["real_std"] = statistics.stdev(real_times) if len(real_times) > 1 else 0.0
    stats["user_mean"] = statistics.mean(user_times)
    stats["user_std"] = statistics.stdev(user_times) if len(user_times) > 1 else 0.0
    stats["sys_mean"]  = statistics.mean(sys_times)
    stats["sys_std"]  = statistics.stdev(sys_times) if len(sys_times) > 1 else 0.0

    return stats

def print_stats(file_name, stats1, stats2, dir1_label, dir2_label):
    """
    Prints a side-by-side comparison of statistics.
    """
    print(f"Comparison for file: {file_name}")
    
    if stats1 is None:
        print(f"  [{dir1_label}] No valid timing data found.")
    else:
        print(f"  [{dir1_label}] Real: mean = {stats1['real_mean']:.3f}, std = {stats1['real_std']:.3f}")
        print(f"            User: mean = {stats1['user_mean']:.3f}, std = {stats1['user_std']:.3f}")
        print(f"             Sys: mean = {stats1['sys_mean']:.3f}, std = {stats1['sys_std']:.3f}")
        
    if stats2 is None:
        print(f"  [{dir2_label}] No valid timing data found.")
    else:
        print(f"  [{dir2_label}] Real: mean = {stats2['real_mean']:.3f}, std = {stats2['real_std']:.3f}")
        print(f"            User: mean = {stats2['user_mean']:.3f}, std = {stats2['user_std']:.3f}")
        print(f"             Sys: mean = {stats2['sys_mean']:.3f}, std = {stats2['sys_std']:.3f}")
    print("-" * 60)

def main():
    parser = argparse.ArgumentParser(
        description="Compare common .txt log files in two directories by computing timing statistics."
    )
    parser.add_argument("dir1", help="Path to the first directory.")
    parser.add_argument("dir2", help="Path to the second directory.")
    args = parser.parse_args()

    # Check that both paths are directories
    if not os.path.isdir(args.dir1):
        print(f"Error: {args.dir1} is not a valid directory.")
        sys.exit(1)
    if not os.path.isdir(args.dir2):
        print(f"Error: {args.dir2} is not a valid directory.")
        sys.exit(1)

    print(f"Searching for .txt files in:\n  Directory 1: {args.dir1}\n  Directory 2: {args.dir2}\n")

    # Map file names to their full paths; using lower-case file names for comparison
    txt_files1 = {f.lower(): os.path.join(args.dir1, f) for f in os.listdir(args.dir1)
                  if f.lower().endswith(".txt")}
    txt_files2 = {f.lower(): os.path.join(args.dir2, f) for f in os.listdir(args.dir2)
                  if f.lower().endswith(".txt")}

    # Find the intersection of common file names
    common_files = set(txt_files1.keys()).intersection(set(txt_files2.keys()))
    
    if not common_files:
        print("No common .txt files were found between the two directories.")
        sys.exit(0)
        
    print(f"Found {len(common_files)} common .txt file(s).\n")
    
    # Compare each common file
    for file_name in sorted(common_files):
        path1 = txt_files1[file_name]
        path2 = txt_files2[file_name]
        
        stats1 = compute_stats(path1)
        stats2 = compute_stats(path2)
        
        print_stats(file_name, stats1, stats2, "Directory1", "Directory2")

if __name__ == "__main__":
    main()
