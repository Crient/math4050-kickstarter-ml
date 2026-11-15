"""Execute a notebook with this Python environment, saving outputs even on failure."""
import argparse
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('notebook', choices=['analysis', 'prep'])
args = parser.parse_args()
path = ROOT/'code'/('02_analysis_and_prediction.ipynb' if args.notebook == 'analysis' else '01_data_prep.ipynb')
notebook = nbformat.read(path, as_version=4)
# A temporary kernelspec ensures the notebook uses this exact venv, not a global
# kernel with a similar display name. Nothing is installed in the user's home.
with TemporaryDirectory(prefix='kickstarter-kernel-') as directory:
    spec = Path(directory)/'kickstarter-project'
    spec.mkdir()
    (spec/'kernel.json').write_text(__import__('json').dumps({
        'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
        'display_name':'Kickstarter project', 'language':'python',
        'env':{'MPLCONFIGDIR':str(ROOT/'.cache/matplotlib')},
    }))
    manager = KernelSpecManager(kernel_dirs=[directory])
    from jupyter_client import KernelManager
    kernel = KernelManager(kernel_name='kickstarter-project', kernel_spec_manager=manager)
    try:
        NotebookClient(notebook, timeout=1800, km=kernel,
                       on_cell_start=lambda cell, cell_index: print(f'Cell {cell_index+1}/{len(notebook.cells)}: {cell.cell_type}', flush=True),
                       resources={'metadata':{'path':str(ROOT)}}).execute()
    finally:
        nbformat.write(notebook, path)
        if kernel.has_kernel:
            kernel.shutdown_kernel(now=True)
print(f'Executed {path.relative_to(ROOT)} using {sys.executable}')
