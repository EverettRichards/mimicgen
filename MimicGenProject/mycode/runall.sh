#!/bin/bash
#set -e

cd "$(dirname "$0")"

# Default values
NOISES=""
NUM_TRIALS=100
DIFF=0
ENV="SQUARE"
FILENAME="output.csv"

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --noises) NOISES="$2"; shift ;;
        --n) NUM_TRIALS="$2"; shift ;;
        --task) TASK="$2"; shift ;;
        --diff) DIFF="$2"; shift ;;
        --env) ENV="$2"; shift ;;
        --filename) FILENAME="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "[INFO] Noise levels: $NOISES"
echo "[INFO] Num trials: $NUM_TRIALS"

# Step 1: Generate noisy .hdf5 files
echo "[1] Generating noisy demos for $TASK"
python noise.py "$NOISES" "$TASK" "$DIFF"


# Step 2: Prepare each dataset with MimicGen
echo "[2] Preparing source datasets..."
i=0
for f in ../mimicgen/datasets/source/${TASK}_noisy_*.hdf5; do
  echo "  Preparing: $f"
  python ../mimicgen/mimicgen/scripts/prepare_src_dataset.py \
    --dataset "$f" \
    --env_interface "MG_$ENV" \
    --env_interface_type robosuite &
done

wait # Await completion...


# Step 3: Generate config files
echo "[3] Creating config files..."
python setup_configs.py "$NUM_TRIALS" "$TASK" "$DIFF"

# Step 4: Run MimicGen in parallel
echo "[4] Running data generation..."
for cfg in /tmp/core_configs/demo_src_${TASK}_task_D${DIFF}_noisy_*.json; do
  echo "  Launching: $cfg"
  python ../mimicgen/mimicgen/scripts/generate_dataset.py \
    --config "$cfg" \
    --auto-remove-exp &
done

wait # Await completion...

# Step 5: Save the outputs to a .csv file
python output.py "$NOISES" "$TASK" "$DIFF" "$FILENAME"

echo "[✓] All done."
