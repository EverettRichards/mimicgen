#!/bin/bash
cd "$(dirname "$0")"

bash runall.sh  \
    --n 100 \
    --noises 0.005,0.015,0.025,0.035,0.04,0.045 \
    --env ThreePieceAssembly \
    --task three_piece_assembly \
    --diff 1 \
    --filename TPA_superlow

bash runall.sh  \
    --n 100 \
    --noises 0.075,0.125,0.175,0.20,0.225,0.375 \
    --env ThreePieceAssembly \
    --task three_piece_assembly \
    --diff 1 \
    --filename TPA_midrange

bash runall.sh  \
    --n 100 \
    --noises 0.005,0.015,0.025,0.035,0.04,0.045 \
    --env NutAssembly \
    --task nut_assembly \
    --diff 0 \
    --filename Nut_superlow

bash runall.sh  \
    --n 100 \
    --noises 0.075,0.125,0.175,0.20,0.225,0.375 \
    --env NutAssembly \
    --task nut_assembly \
    --diff 0 \
    --filename Nut_midrange

bash runall.sh  \
    --n 100 \
    --noises 0.005,0.015,0.025,0.035,0.04,0.045 \
    --env StackThree \
    --task stack_three \
    --diff 1 \
    --filename Stack3_superlow

bash runall.sh  \
    --n 100 \
    --noises 0.075,0.125,0.175,0.20,0.225,0.375 \
    --env StackThree \
    --task stack_three \
    --diff 1 \
    --filename Stack3_midrange

bash runall.sh  \
    --n 100 \
    --noises 0.005,0.015,0.025,0.035,0.04,0.045 \
    --env Coffee \
    --task coffee \
    --diff 1 \
    --filename Coffee_superlow

bash runall.sh  \
    --n 100 \
    --noises 0.075,0.125,0.175,0.20,0.225,0.375 \
    --env Coffee \
    --task coffee \
    --diff 1 \
    --filename Coffee_midrange

bash runall.sh  \
    --n 100 \
    --noises 0.005,0.015,0.025,0.035,0.04,0.045 \
    --env Square \
    --task square \
    --diff 1 \
    --filename Square_superlow

bash runall.sh  \
    --n 100 \
    --noises 0.075,0.125,0.175,0.20,0.225,0.375 \
    --env Square \
    --task square \
    --diff 1 \
    --filename Square_midrange

bash runall.sh  \
    --n 100 \
    --noises 0.005,0.015,0.025,0.035,0.04,0.045 \
    --env Kitchen \
    --task kitchen \
    --diff 1 \
    --filename Kitchen_superlow

bash runall.sh  \
    --n 100 \
    --noises 0.075,0.125,0.175,0.20,0.225,0.375 \
    --env Kitchen \
    --task kitchen \
    --diff 1 \
    --filename Kitchen_midrange