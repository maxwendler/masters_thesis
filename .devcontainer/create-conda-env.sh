#!/bin/bash

conda create -p /workspaces/ma-max-wendler/.conda --file /workspaces/ma-max-wendler/.devcontainer/conda-requirements.txt -c conda-forge -y
conda init zsh
conda init bash
echo "conda activate /workspaces/ma-max-wendler/.conda" >> ~/.zshrc
echo "conda activate /workspaces/ma-max-wendler/.conda" >> ~/.bashrc