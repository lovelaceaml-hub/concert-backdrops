# Source this from the repository root before local renders.
SOL3_ROOT="$(pwd)"
export SONG=sol_v3
export AUDIO="$SOL3_ROOT/work/sol3/sol-v3-score.wav"
export FEATURES="$SOL3_ROOT/work/sol3/features.npz"
export OUT_RES=1080p
export OUT_FPS=60
export LIBGL_ALWAYS_SOFTWARE=1
export P3D_CACHE="$SOL3_ROOT/work/sol3/cache"
export LP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MESA_SHADER_CACHE_DIR=/tmp/mesa-sol3
export NUMBA_CACHE_DIR=/tmp/numba-sol3
