import os
import re
import numpy as np
from collections import defaultdict

BASE_DIR = "./"  # Change if needed
FOLDER_PREFIX = "spec_log_new_"
NUM_FOLDERS = 20
TOTAL_TIME_PATTERN = re.compile(r"total time\s*:\[(\d+)\]")

# Data structures
cheri_data = defaultdict(list)
blinded_data = defaultdict(list)
baseline_data = defaultdict(list)

def classify_file(filename):
    """Classify file type and normalize key so report shows algorithm + size."""
    if "cheri_blinded" in filename:
        key = filename.replace("_spec_cheri_blinded", "")
        return "blinded", key
    elif "cheri" in filename and "blinded" not in filename:
        key = filename.replace("_spec_cheri", "")
        return "cheri", key
    elif "baseline" in filename:
        key = filename.replace("_spec_baseline", "")
        return "baseline", key
    else:
        return None, None

# Parse logs
for i in range(1, NUM_FOLDERS + 1):
    folder_path = os.path.join(BASE_DIR, f"{FOLDER_PREFIX}{i}")
    if not os.path.isdir(folder_path):
        print(f"Warning: {folder_path} missing")
        continue

    for filename in os.listdir(folder_path):
        if not filename.endswith(".elf.txt"):
            continue
        ftype, key = classify_file(filename)
        if not key:
            continue

        filepath = os.path.join(folder_path, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            match = TOTAL_TIME_PATTERN.search(content)
            if match:
                value = int(match.group(1))
                if ftype == "cheri":
                    cheri_data[key].append(value)
                elif ftype == "blinded":
                    blinded_data[key].append(value)
                elif ftype == "baseline":
                    baseline_data[key].append(value)

# Final report
print("Algorithm_Size, Baseline Mean, Baseline Std, Baseline Std%, "
      "CHERI Mean, CHERI Std, CHERI Std%, "
      "Blinded Mean, Blinded Std, Blinded Std%, "
      "Delta(Blinded-CHERI), % Delta(Blinded-CHERI), "
      "Delta(CHERI-Baseline), % Delta(CHERI-Baseline)")

for key in sorted(set(cheri_data) & set(blinded_data) & set(baseline_data)):
    cheri_times = cheri_data[key]
    blinded_times = blinded_data[key]
    baseline_times = baseline_data[key]

    if len(cheri_times) < 2 or len(blinded_times) < 2 or len(baseline_times) < 2:
        continue

    # Stats
    baseline_mean = np.mean(baseline_times)
    baseline_std = np.std(baseline_times)
    baseline_std_pct = (baseline_std / baseline_mean) * 100

    cheri_mean = np.mean(cheri_times)
    cheri_std = np.std(cheri_times)
    cheri_std_pct = (cheri_std / cheri_mean) * 100

    blinded_mean = np.mean(blinded_times)
    blinded_std = np.std(blinded_times)
    blinded_std_pct = (blinded_std / blinded_mean) * 100

    # Deltas
    delta_blinded_cheri = blinded_mean - baseline_mean
    percent_delta_blinded_cheri = (delta_blinded_cheri / baseline_mean) * 100

    delta_cheri_baseline = cheri_mean - baseline_mean
    percent_delta_cheri_baseline = (delta_cheri_baseline / baseline_mean) * 100

    # Clean label -> remove .elf.txt
    label = key.replace(".elf.txt", "")
    print(f"{label}, {baseline_mean:.2f}, {baseline_std:.2f}, {baseline_std_pct:.2f}%, "
          f"{cheri_mean:.2f}, {cheri_std:.2f}, {cheri_std_pct:.2f}%, "
          f"{blinded_mean:.2f}, {blinded_std:.2f}, {blinded_std_pct:.2f}%, "
          f"{delta_blinded_cheri:.2f}, {percent_delta_blinded_cheri:.2f}%, "
          f"{delta_cheri_baseline:.2f}, {percent_delta_cheri_baseline:.2f}%")
