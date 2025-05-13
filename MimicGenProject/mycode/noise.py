import h5py
import numpy as np
import shutil
import os
import glob
import sys

# Noise levels (customize this!)
# noises = [0.15,0.20,0.25,0.50,0.75,1.00]
noise_str = sys.argv[1] if len(sys.argv) > 1 else "0.01,0.02,0.05"
task = sys.argv[2]
difficulty = sys.argv[3]
noises = [float(x) for x in noise_str.split(",")]

original_path = f"../mimicgen/datasets/source/{task}.hdf5"
output_dir = "../mimicgen/datasets/source"
os.makedirs(output_dir, exist_ok=True)

# Step 1: Remove old noisy Source files

old_files = glob.glob(f"{output_dir}/{task}_noisy_*.hdf5")
for f in old_files:
    os.remove(f)
    print(f"[✗] Removed old: {f}")

# Optional: Remove old MimicGen output folders

output_root = f"/tmp/core_datasets/{task}"
for i in range(20):  # assumes max 20 noise levels
    folder = f"{output_root}/{task}_D{difficulty}_noisy_{i}"
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print(f"[✗] Removed old output: {folder}")


# Step 2: Create new noisy files
for i, noise_level in enumerate(noises):
    new_path = f"{output_dir}/{task}_noisy_{i}.hdf5"
    shutil.copyfile(original_path, new_path)
    print(f"[✓] Copied to: {new_path}")

    with h5py.File(new_path, "r+") as f:
        for key in f["data"].keys():
            actions = f[f"data/{key}/actions"][:]
            noise = np.random.normal(scale=noise_level, size=actions.shape)
            f[f"data/{key}/actions"][:] = actions + noise
    print(f"[✓] Added noise (scale={noise_level}) to: {new_path}")
