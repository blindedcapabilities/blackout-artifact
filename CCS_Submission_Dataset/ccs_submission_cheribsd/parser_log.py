#!/usr/bin/env python3
import os
import re
import sys
import statistics
import argparse

def process_file(filename):
    """
    Process a single file: extract timing numbers, compute mean and std.
    """
    real_times = []
    user_times = []
    sys_times = []
    
    # Regex pattern to match lines like:
    # "1.05 real         0.77 user         0.22 sys"
    pattern = re.compile(r"(\d+\.\d+)\s+real\s+(\d+\.\d+)\s+user\s+(\d+\.\d+)\s+sys")
    
    try:
        with open(filename, "r") as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    real_times.append(float(match.group(1)))
                    user_times.append(float(match.group(2)))
                    sys_times.append(float(match.group(3)))
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return
    
    # If no valid data is found, report it
    if not real_times:
        print(f"No valid timing data found in {filename}.\n")
        return

    # Compute statistics (if there's only one value, set std to 0)
    real_mean = statistics.mean(real_times)
    real_std = statistics.stdev(real_times) if len(real_times) > 1 else 0.0

    user_mean = statistics.mean(user_times)
    user_std = statistics.stdev(user_times) if len(user_times) > 1 else 0.0

    sys_mean = statistics.mean(sys_times)
    sys_std = statistics.stdev(sys_times) if len(sys_times) > 1 else 0.0

    # Print the results for this file
    print(f"Statistics for {os.path.basename(filename)}:")
    print("  Real time: mean = {:.3f}, std = {:.3f}".format(real_mean, real_std))
    print("  User time: mean = {:.3f}, std = {:.3f}".format(user_mean, user_std))
    print("  Sys time : mean = {:.3f}, std = {:.3f}".format(sys_mean, sys_std))
    print()

def main():
    # Set up argument parsing so the user provides the directory path
    parser = argparse.ArgumentParser(
        description="Process .txt files containing timing info and compute statistics."
    )
    parser.add_argument(
        "path",
        metavar="DIR",
        type=str,
        help="The directory containing .txt log files.",
    )
    args = parser.parse_args()

    # Verify that the given path is a directory
    if not os.path.isdir(args.path):
        print(f"Error: {args.path} is not a valid directory.")
        sys.exit(1)
    
    # Debug print: show the directory being processed
    print(f"Searching in directory: {args.path}")
    
    # Get a list of all .txt files in the directory (case-insensitive)
    txt_files = [
        os.path.join(args.path, filename)
        for filename in os.listdir(args.path)
        if filename.lower().endswith(".txt")
    ]

    # Debug print: number of files found
    if not txt_files:
        print("No .txt files found in the specified directory.")
        sys.exit(0)
    else:
        print(f"Found {len(txt_files)} .txt file(s).\n")

    # Process each file
    for txt_file in txt_files:
        process_file(txt_file)

if __name__ == "__main__":
    main()
