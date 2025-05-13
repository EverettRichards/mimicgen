import json
import glob
import os
import sys

NUM_TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
task = sys.argv[2]
difficulty = sys.argv[3]

noisy_paths = sorted(glob.glob(f"../mimicgen/datasets/source/{task}_noisy_*.hdf5"))

for i, path in enumerate(noisy_paths):
    base_path = f"/tmp/core_configs/demo_src_{task}_task_D{difficulty}.json"
    out_path = f"/tmp/core_configs/demo_src_{task}_task_D{difficulty}_noisy_{i}.json"

    with open(base_path, "r") as f:
        config = json.load(f)

    # Update dataset path and experiment name
    config["experiment"]["source"]["dataset_path"] = os.path.abspath(path)
    config["experiment"]["name"] = f"{task}_D{difficulty}_noisy_{i}"
    
    config["experiment"]["render_video"] = False
    config["experiment"]["num_demo_to_render"] = 0
    config["experiment"]["num_fail_demo_to_render"] = 0
    
    # Set number of trials dynamically
    config["experiment"]["generation"]["num_trials"] = NUM_TRIALS


    with open(out_path, "w") as f:
        json.dump(config, f, indent=4)

    print(f"[✓] Wrote config: {out_path}")
