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

######################################################################

num_samples = 5
max_concurrent_samples = 5

instructions = [
    [("kitchen","Kitchen","1"),[0.00,0.01,0.02]],
    [("coffee","Coffee","1"),[0.05,0.10,0.15]],
]

source_dir = "../mimicgen/datasets/source"

######################################################################

def clearOldFiles(task,difficulty,noise_clean):
    # Step 1: Prepare the source files and remove old files
    original_path = f"../mimicgen/datasets/source/{task}.hdf5"
    os.makedirs(source_dir, exist_ok=True)


    # Remove the existing source file if it exists
    old_file = f"{source_dir}/{task}_noise_{noise_clean}.hdf5"
    if os.path.exists(old_file):
        os.remove(old_file)
        print(f"[✗] Removed old: {old_file}")

    # Remove old MimicGen output folders
    output_root = f"/tmp/core_datasets/{task}"
    folder = f"{output_root}/{task}_D{difficulty}_noise_{noise_clean}"
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print(f"[✗] Removed old output: {folder}")
    
    # Step 2: Create new noisy files
    new_path = f"{source_dir}/{task}_noise_{noise_clean}.hdf5"
    shutil.copyfile(original_path, new_path)
    print(f"[✓] Copied to: {new_path}")
    
    return new_path

#############################################################################

def addNoise(new_path, noise):
    # Add the noise to each action
    with h5py.File(new_path, "r+") as f:
        for key in f["data"].keys():
            actions = f[f"data/{key}/actions"][:]
            injected_noise = np.random.normal(scale=noise, size=actions.shape)
            f[f"data/{key}/actions"][:] = actions + injected_noise
    print(f"[✓] Added noise (scale={noise}) to: {new_path}")

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
    
    print(f"[✓] Prepared source dataset: {file_name}")

#############################################################################

def setupConfigs(task,difficulty,noise_clean,source_file):

    # noisy_paths = sorted(glob.glob(f"../mimicgen/datasets/source/{task}_noisy_*.hdf5"))
    # for i, path in enumerate(noisy_paths):

    base_path = f"/tmp/core_configs/demo_src_{task}_task_D{difficulty}.json"
    out_path = f"/tmp/core_configs/demo_src_{task}_task_D{difficulty}_noise_{noise_clean}.json"

    with open(base_path, "r") as f:
        config = json.load(f)

    # Update dataset path and experiment name
    config["experiment"]["source"]["dataset_path"] = os.path.abspath(source_file)
    config["experiment"]["name"] = f"{task}_D{difficulty}_noise_{noise_clean}"
    
    config["experiment"]["render_video"] = False
    config["experiment"]["num_demo_to_render"] = 0
    config["experiment"]["num_fail_demo_to_render"] = 0
    
    # Set number of trials dynamically
    config["experiment"]["generation"]["num_trials"] = num_samples

    with open(out_path, "w") as f:
        json.dump(config, f, indent=4)

    print(f"[✓] Wrote config: {out_path}")
    
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
    print(f"[✓] Generated dataset: {config_file}")

    data_file = f"/tmp/core_datasets/{task}/{task}_D{difficulty}_noise_{noise_clean}/important_stats.json"
    with open(data_file) as f:
        stats = json.load(f)
        return stats.get("num_success","0"), stats.get("num_failures","0")
    return "0","0"
    print(f"[✓] Generated dataset: {data_file}")

#############################################################################

def outputResults(task,difficulty,noise,successes,failures):

    output_dir = "../data_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Open output_dir/{task}_D{difficulty}.csv using Pandas
    output_file = f"{output_dir}/{task}_D{difficulty}.csv"
    
    # IF THE FILE EXISTS, open the CSV file and read it into a DataFrame
    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
        print(f"[✓] Found existing CSV file: {output_file}")
    else:
        # Create a new DataFrame with the specified columns
        df = pd.DataFrame(columns=["noise", "success", "fail"])
        print(f"[✓] Created new CSV file: {output_file}")
    # Add a new row to the DataFrame
    new_row = {
        "noise": noise,
        "success": successes,
        "fail": failures,
    }

    # Add the row to the DataFrame, and sort by noise ascending
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = df.sort_values(by=["noise"], ascending=True)

    # Save the dataframe to the CSV file (assume df already updated)
    df.to_csv(output_file, index=False)
    print(f"[✓] Output results to: {output_file}")

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

    print(f"[...] Generating dataset for {task} with noise level: {noise}")
    successes,failures = generateDataset(config_file, task, difficulty, noise_clean)
    
    outputResults(task,difficulty,noise,successes,failures)

    print(f"[✓] Finished processing {task} with noise levels: {noise}")

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

# Use subprocesses to run five instructions concurrently at a time, eventually getting through all instruction_list

def worker(task_id):
    print(f"Worker {task_id} started.")

while True:
    # Check if all instructions are complete
    if all(complete_list):
        print("[✓] All instructions completed.")
        break

    # Get the next batch of instructions to run
    processes = []
    for i in range(len(instruction_list)):
        if not complete_list[i]:
            instruction = instruction_list[i]
            print(f"[✓] Running instruction {i+1}/{len(instruction_list)}: {instruction}")
            
            def process_task(instruction, index):
                executeInstruction(instruction)
                complete_list[index] = True
            
            p = Process(target=process_task, args=(instruction, i))
            p.start()
            processes.append(p)
            
            if len(processes) >= max_concurrent_samples:
                break

    # Wait for the processes to finish
    for p in processes:
        p.join()

    # Wait for the processes to finish
    for p in processes:
        p.wait()