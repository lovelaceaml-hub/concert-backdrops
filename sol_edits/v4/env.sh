# Source from the repository root. Analysis uses the original scene clock.
SOL4_ROOT="$(pwd)"
export AUDIO="$SOL4_ROOT/work/sol4/Nine-Colours-original-medley.wav"
export FEATURES="$SOL4_ROOT/work/sol4/features.npz"
export OUT_FPS=60 OUT_RES=1080p LIBGL_ALWAYS_SOFTWARE=1
export P3D_CACHE="$SOL4_ROOT/work/sol4/cache"
export LP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export MESA_SHADER_CACHE_DIR=/tmp/mesa-sol4
export NUMBA_CACHE_DIR=/tmp/numba-sol4
