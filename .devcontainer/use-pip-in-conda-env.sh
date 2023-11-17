#!/bin/bash

conda activate /workspaces/ma-max-wendler/.conda
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r /workspaces/ma-max-wendler/.devcontainer/pip-requirements.txt
conda deactivate