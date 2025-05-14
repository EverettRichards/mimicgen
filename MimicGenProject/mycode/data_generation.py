import h5py
import numpy as np
import shutil
import os
import glob
import math
import sys
import subprocess
import json
import pandas as pd
from multiprocessing import Process
from multiprocessing import Semaphore
import time
from colorama import Fore, Style, Back

######################################################################

num_samples = 100
max_concurrent_samples = 6

debug_mode = False
show_progress = False

# pg.32

all_noises = [0.000,0.005,0.010,0.015,0.02,0.025,0.03,0.035,0.04,0.045,0.05,0.075,0.100,0.125,0.150,0.175,0.200,0.225,0.250,0.275,0.300,0.325,0.350,0.375,0.400,0.425,0.450,0.475,0.500,1.000]

instructions = [
    # [("stack","Stack","0"),all_noises],
    [("hammer_cleanup","HammerCleanup","D0"),all_noises],
    [("pick_place","PickPlace","D0"),all_noises],
    [("coffee_preparation","CoffeePreparation","D1"),all_noises],
    [("mug_cleanup","MugCleanup","D1"),all_noises],
    [("threading","Threading","D2"),all_noises],
]

source_dir = "../mimicgen/datasets/source"

######################################################################

def debug(txt):
    if debug_mode:
        print(Fore.YELLOW + f"{txt}" + Style.RESET_ALL)

def checkpoint(txt):
    if show_progress:
        print(Fore.CYAN + f"{txt}" + Style.RESET_ALL)

def err(txt):
    print(Fore.RED + f"{txt}" + Style.RESET_ALL)

#####################################################################

def clearOldFiles(task,difficulty,noise_clean):
    # Step 1: Prepare the source files and remove old files
    original_path = f"../mimicgen/datasets/source/{task}.hdf5"
    os.makedirs(source_dir, exist_ok=True)


    # Remove the existing source file if it exists
    old_file = f"{source_dir}/{task}_noise_{noise_clean}.hdf5"
    if os.path.exists(old_file):
        os.remove(old_file)
        debug(f"[✗] Removed old: {old_file}")

    # Remove old MimicGen output folders
    output_root = f"/tmp/core_datasets/{task}"
    folder = f"{output_root}/{task}_{difficulty}_noise_{noise_clean}"
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        debug(f"[✗] Removed old output: {folder}")
    
    # Step 2: Create new noisy files
    new_path = f"{source_dir}/{task}_noise_{noise_clean}.hdf5"
    shutil.copyfile(original_path, new_path)
    debug(f"[✓] Created Blank Noisy File: {new_path}")
    
    return new_path

#############################################################################

def addNoise(new_path, noise):
    # Add the noise to each action
    with h5py.File(new_path, "r+") as f:
        for key in f["data"].keys():
            actions = f[f"data/{key}/actions"][:]
            injected_noise = np.random.normal(scale=noise, size=actions.shape)
            f[f"data/{key}/actions"][:] = actions + injected_noise
    debug(f"[✓] Added noise (scale={noise}) to: {new_path}")

#############################################################################

def prepareSourceDataset(file_name, environment):
    # for f in ../mimicgen/datasets/source/${TASK}_noisy_*.hdf5; do

    command = [
        "python",
        "../mimicgen/mimicgen/scripts/prepare_src_dataset.py",
        "--dataset", file_name,
        "--env_interface", f"MG_{environment}",
        "--env_interface_type", "robosuite"
    ]

    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    checkpoint(f"[✓] Prepared source dataset: {file_name}")

#############################################################################

def setupConfigs(task,difficulty,noise_clean,source_file):

    # noisy_paths = sorted(glob.glob(f"../mimicgen/datasets/source/{task}_noisy_*.hdf5"))
    # for i, path in enumerate(noisy_paths):

    base_path = f"/tmp/core_configs/demo_src_{task}_task_{difficulty}.json"
    out_path = f"/tmp/core_configs/demo_src_{task}_task_{difficulty}_noise_{noise_clean}.json"

    with open(base_path, "r") as f:
        config = json.load(f)

    # Update dataset path and experiment name
    config["experiment"]["source"]["dataset_path"] = os.path.abspath(source_file)
    config["experiment"]["name"] = f"{task}_{difficulty}_noise_{noise_clean}"
    
    config["experiment"]["render_video"] = False
    config["experiment"]["num_demo_to_render"] = 0
    config["experiment"]["num_fail_demo_to_render"] = 0
    
    # Set number of trials dynamically
    config["experiment"]["generation"]["num_trials"] = num_samples

    with open(out_path, "w") as f:
        json.dump(config, f, indent=4)

    debug(f"[✓] Wrote config: {out_path}")
    
    return out_path

#############################################################################

def generateDataset(config_file, task, difficulty, noise_clean):
    command = [
        "python",
        "../mimicgen/mimicgen/scripts/generate_dataset.py",
        "--config", config_file,
        "--auto-remove-exp",
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    data_file = f"/tmp/core_datasets/{task}/{task}_{difficulty}_noise_{noise_clean}/important_stats.json"
    try:
        with open(data_file) as f:
            stats = json.load(f)
            return stats.get("num_success","0"), stats.get("num_failures","0")
    except FileNotFoundError:
        err(f"[✗] ERROR: File not found: {data_file}")
        return "0","0"

    checkpoint(f"[✓] Generated dataset: {data_file}")

#############################################################################

def outputResults(task,difficulty,noise,successes,failures):

    output_dir = "../data_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Open output_dir/{task}_{difficulty}.csv using Pandas
    output_file = f"{output_dir}/{task}_{difficulty}.csv"
    
    # IF THE FILE EXISTS, open the CSV file and read it into a DataFrame
    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
        debug(f"[✓] Found existing CSV file: {output_file}")
    else:
        # Create a new DataFrame with the specified columns
        df = pd.DataFrame(columns=["noise", "success", "fail"])
        debug(f"[✓] Created new CSV file: {output_file}")
    # Add a new row to the DataFrame
    new_row = {
        "noise": noise,
        "success": successes,
        "fail": failures,
    }

    # Add the row to the DataFrame, and sort by noise ascending
    # If the noise is already in the DataFrame, update the row instead
    
    if noise in df["noise"].values:
        df.loc[df["noise"] == noise, ["success_rate", "fail_rate"]] = [successes, failures]
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df = df.sort_values(by=["noise"], ascending=True)

    # Save the dataframe to the CSV file (assume df already updated)
    df.to_csv(output_file, index=False)
    checkpoint(f"[✓] Output results to: {output_file}")

#############################################################################

def executeInstruction(instruction):
    task_items,noise = instruction
    task, environment, difficulty = task_items
    noise_clean = math.floor(noise*1000)

    source_file = clearOldFiles(task,difficulty,noise_clean)
    addNoise(source_file, noise)

    # Use the subprocess to run the prepare_src_dataset.py script
    prepareSourceDataset(source_file, environment)

    config_file = setupConfigs(task,difficulty,noise_clean,source_file)
    debug(f"[...] Generating dataset for {task} with noise level: {noise}")
    successes,failures = generateDataset(config_file, task, difficulty, noise_clean)
    
    outputResults(task,difficulty,noise,successes,failures)

    print(Fore.GREEN + f"[✓] Finished processing {task} with noise levels: {noise}")

#############################################################################

def generateInstructionList(instructions):
    instruction_list = []
    for instruction in instructions:
        for noise in instruction[1]:
            instruction_list.append((instruction[0],noise))
    return instruction_list

#############################################################################

instruction_list = generateInstructionList(instructions)
complete_list = [False]*len(instruction_list)
current_file = os.path.abspath(sys.argv[0])

print("ROUGH ETA:", round(len(instruction_list) * num_samples / 100 / max_concurrent_samples + .06,2), "hours")

start_time = time.time()
print(Fore.BLUE + f"[✓] Starting data generation with {max_concurrent_samples} concurrent processes at time {start_time}." + Style.RESET_ALL)

# Use subprocesses to run five instructions concurrently at a time, eventually getting through all instruction_list

def worker(task_id):
    print(f"Worker {task_id} started.")

# Semaphore to limit the number of active processes
semaphore = Semaphore(max_concurrent_samples)

def process_task(instruction, index):
    with semaphore:
        print(f"[✓] Running instruction {index+1}/{len(instruction_list)}: {instruction}")
        executeInstruction(instruction)
        complete_list[index] = True
        # print(complete_list)

# Start processing instructions
for i in range(len(instruction_list)):
    if not complete_list[i]:
        instruction = instruction_list[i]
        
        p = Process(target=process_task, args=(instruction, i))
        p.start()

# Wait for all processes to complete
while not all(complete_list):
    pass

end_time = time.time()
elapsed_time = end_time - start_time
print(f"[✓] All tasks completed in {elapsed_time:.2f} seconds.")