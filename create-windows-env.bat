conda env create -f environment-windows.yml
conda activate gcs

pip install --find-links=./igraph-whl python-igraph
