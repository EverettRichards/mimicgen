#!/bin/bash
cd "$(dirname "$0")"

# Fill in prior gaps
bash runall.sh  \
    --n 100 \
    --noises 0.04,0.045,0.05,0.075,0.10 \
    --env StackThree \
    --task stack_three \
    --diff 1 \
    --filename Stack3_fixed_0.05ish

bash runall.sh  \
    --n 100 \
    --noises 0.275,0.30,0.325,0.350 \
    --env ThreePieceAssembly \
    --task three_piece_assembly \
    --diff 1 \
    --filename TPA_mid_ext_low

bash runall.sh  \
    --n 100 \
    --noises 0.40,0.425,0.450,0.475 \
    --env ThreePieceAssembly \
    --task three_piece_assembly \
    --diff 1 \
    --filename TPA_mid_ext_high

bash runall.sh  \
    --n 100 \
    --noises 0.275,0.30,0.325,0.350 \
    --env NutAssembly \
    --task nut_assembly \
    --diff 0 \
    --filename Nut_mid_ext_low

bash runall.sh  \
    --n 100 \
    --noises 0.40,0.425,0.450,0.475 \
    --env NutAssembly \
    --task nut_assembly \
    --diff 0 \
    --filename Nut_mid_ext_high

bash runall.sh  \
    --n 100 \
    --noises 0.275,0.30,0.325,0.350 \
    --env StackThree \
    --task stack_three \
    --diff 1 \
    --filename Stack3_mid_ext_low

bash runall.sh  \
    --n 100 \
    --noises 0.40,0.425,0.450,0.475 \
    --env StackThree \
    --task stack_three \
    --diff 1 \
    --filename Stack3_mid_ext_high

bash runall.sh  \
    --n 100 \
    --noises 0.275,0.30,0.325,0.350 \
    --env Coffee \
    --task coffee \
    --diff 1 \
    --filename Coffee_mid_ext_low

bash runall.sh  \
    --n 100 \
    --noises 0.40,0.425,0.450,0.475 \
    --env Coffee \
    --task coffee \
    --diff 1 \
    --filename Coffee_mid_ext_high

bash runall.sh  \
    --n 100 \
    --noises 0.275,0.30,0.325,0.350 \
    --env Square \
    --task square \
    --diff 1 \
    --filename Square_mid_ext_low

bash runall.sh  \
    --n 100 \
    --noises 0.40,0.425,0.450,0.475 \
    --env Square \
    --task square \
    --diff 1 \
    --filename Square_mid_ext_high

bash runall.sh  \
    --n 100 \
    --noises 0.275,0.30,0.325,0.350 \
    --env Kitchen \
    --task kitchen \
    --diff 1 \
    --filename Kitchen_mid_ext_low

bash runall.sh  \
    --n 100 \
    --noises 0.40,0.425,0.450,0.475 \
    --env Kitchen \
    --task kitchen \
    --diff 1 \
    --filename Kitchen_mid_ext_high