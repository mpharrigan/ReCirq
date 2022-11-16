from pathlib import Path
from subprocess import run

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

SRC_DIR = Path(__file__).parent / '..'


def execute_notebook(notebook_path: str):
    """Execute a jupyter notebook in this directory.
    Args:
        name: The name of the notebook without extension.
    """
    with (SRC_DIR / notebook_path).open() as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    ep.preprocess(nb)


NBS = ['docs/benchmarks/rabi_oscillations.ipynb',
       'docs/fermi_hubbard/experiment_example.ipynb',
       'docs/fermi_hubbard/publication_results.ipynb',
       'docs/ftbbl.ipynb',
       'docs/guide/data_analysis.ipynb',
       'docs/guide/data_collection.ipynb',
       'docs/hfvqe/molecular_data.ipynb',
       'docs/hfvqe/quickstart.ipynb',
       'docs/otoc/otoc_example.ipynb',
       'docs/qaoa/binary_paintshop.ipynb',
       'docs/qaoa/example_problems.ipynb',
       'docs/qaoa/hardware_grid_circuits.ipynb',
       'docs/qaoa/landscape_analysis.ipynb',
       'docs/qaoa/optimization_analysis.ipynb',
       'docs/qaoa/precomputed_analysis.ipynb',
       'docs/qaoa/qaoa_ising.ipynb',
       'docs/qaoa/qaoa_maxcut.ipynb',
       'docs/qaoa/routing_with_tket.ipynb',
       'docs/qaoa/tasks.ipynb',
       'docs/time_crystals/time_crystal_circuit_generation.ipynb',
       'docs/toric_code/toric_code_ground_state.ipynb',
       'recirq/otoc/loschmidt/tilted_square_lattice/analysis-walkthrough.ipynb',
       'recirq/otoc/loschmidt/tilted_square_lattice/plots.ipynb',
       'recirq/readout_scan/Readout-Analysis.ipynb',
       'recirq/readout_scan/Readout-Time-Series-Analysis.ipynb'
       ]


def main():
    o = run(['git', 'ls-files'], capture_output=True, universal_newlines=True, cwd=SRC_DIR)
    fns = [line for line in o.stdout.splitlines() if
           line.endswith('.ipynb')]

    print(repr(fns))
    for fn in fns:
        print(fn, flush=True)
        execute_notebook(fn)


if __name__ == '__main__':
    main()
