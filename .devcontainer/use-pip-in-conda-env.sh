#!/bin/bash

conda activate /opt/.conda
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir tle-tools
conda deactivate