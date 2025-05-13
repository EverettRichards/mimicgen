import os
import json
import csv
import sys
from glob import glob
from pathlib import Path

# -----------------------------
# Parse --noises argument
# -----------------------------
task = None

noise_str = sys.argv[1] if len(sys.argv) > 1 else "0.01,0.02,0.05"
task = sys.argv[2]
difficulty = sys.argv[3]
filename = sys.argv[4]
noise_levels = [float(x) for x in noise_str.split(",")]

# -----------------------------
# Setup paths
# -----------------------------
output_dir = os.path.expanduser("~/MimicGenProject/MimicGenProject/outputs")
os.makedirs(output_dir, exist_ok=True)
output_csv = os.path.join(output_dir, f"{filename}.csv")

# Find stats
stats_files = sorted(glob(f"/tmp/core_datasets/{task}/{task}_D{difficulty}_noisy_*/important_stats.json"))

if len(stats_files) != len(noise_levels):
    print(f"[!] Mismatch: found {len(stats_files)} runs but {len(noise_levels)} noise levels.")
    sys.exit(1)

rows = []

# -----------------------------
# Collect stats
# -----------------------------
for i, path in enumerate(stats_files):
    try:
        with open(path) as f:
            stats = json.load(f)
        exp_name = Path(path).parent.name
        row = {
            "run": exp_name,
            "noise": noise_levels[i],
            "successes": stats.get("num_success", "NA"),
            "attempted": stats.get("num_attempts", "NA"),
            "failures": stats.get("num_failures", "NA"),
            "duration": str(float(stats.get("time spent (hrs)", "NA"))*60*60),
            "success_rate": round(
                stats["num_success"] / stats["num_attempts"] * 100, 2
            ) if stats.get("num_attempts") else "NA"
        }
        rows.append(row)
    except Exception as e:
        print(f"[✗] Failed to process {path}: {e}")

# -----------------------------
# Write to CSV
# -----------------------------
fieldnames = ["run", "noise", "success_rate", "successes", "failures", "attempted", "duration"]
with open(output_csv, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"[✓] Summary with noise saved to: {output_csv}")
