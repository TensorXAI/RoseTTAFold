#!/bin/bash

# make the script stop when error (non-true exit code) is occured
set -e

############################################################
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
echo "Initializing Conda..."
# Initialize Conda properly
__conda_setup="$('conda' 'shell.bash' 'hook' 2> /dev/null || true)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    echo "Error: Conda initialization failed."
    exit 1
fi
unset __conda_setup
# <<< conda initialize <<<
############################################################

echo "Activating biox environment..."
conda activate biox || { echo "Error: Failed to activate biox environment."; exit 1; }

echo "Environment activated: $(conda info --envs | grep \*)"
echo "CONDA_PREFIX=$CONDA_PREFIX"

mkdir -p $CONDA_PREFIX/share/blast-2.2.26
ln -s $CONDA_PREFIX/data $CONDA_PREFIX/share/blast-2.2.26/data
export BLASTMAT=$CONDA_PREFIX/share/blast-2.2.26/data

echo "BLASTMAT is set to: $BLASTMAT"
echo "Symlink created: $CONDA_PREFIX/data -> $CONDA_PREFIX/share/blast-2.2.26/data"

# Execute the command passed as arguments
exec "$@"
