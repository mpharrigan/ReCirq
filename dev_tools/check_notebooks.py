import dataclasses
import os
import time
from multiprocessing import Pool
from subprocess import run as _run, CalledProcessError

PACKAGES = [
    # for running the notebooks
    "jupyter",
    # assumed to be part of colab
    "seaborn~=0.11.1",
]


def _check_notebook(notebook_fn, notebook_id, stdout, stderr):
    print(notebook_id)

    def run(*args, **kwargs):
        return _run(*args, check=True, stdout=stdout, stderr=stderr, **kwargs)

    venv_dir = os.path.abspath(f'./notebook_envs/{notebook_id}')
    run(['python', '-m', 'venv', '--clear', venv_dir])

    pip = f'{venv_dir}/bin/pip'
    run([pip, 'install'] + PACKAGES)

    jupyter = f'{venv_dir}/bin/jupyter'
    env = os.environ.copy()
    env['PATH'] = f'{venv_dir}/bin:{env["PATH"]}'
    run([jupyter, 'nbconvert', '--to', 'html', '--execute', notebook_fn], cwd='../', env=env)
    print(notebook_id, 'done', flush=True)


@dataclasses.dataclass(frozen=True)
class NotebookRunResult:
    duration: float


def check_notebook(notebook_fn):
    notebook_id = notebook_fn.replace('/', '-')
    start = time.perf_counter()
    with open(f'./notebook_envs/{notebook_id}.stdout', 'w') as stdout, open(f'./notebook_envs/{notebook_id}.stderr', 'w') as stderr:
        try:
            _check_notebook(notebook_fn, notebook_id, stdout, stderr)
        except CalledProcessError:
            print('!!!', notebook_id)
    end = time.perf_counter()
    print(notebook_id, end-start)
    return NotebookRunResult(
        duration=end-start,
    )


NOTEBOOKS = [
    'docs/otoc/otoc_example.ipynb',
    'docs/guide/data_analysis.ipynb',
    'docs/guide/data_collection.ipynb',
    'docs/qaoa/example_problems.ipynb',
    'docs/qaoa/precomputed_analysis.ipynb',
    'docs/qaoa/hardware_grid_circuits.ipynb',
    'docs/qaoa/optimization_analysis.ipynb',
    'docs/qaoa/tasks.ipynb',
    'docs/qaoa/landscape_analysis.ipynb',
    'docs/qaoa/routing_with_tket.ipynb',
    'docs/quantum_chess/concepts.ipynb',
    # 'docs/quantum_chess/quantum_chess_rest_api.ipynb', # runs a server, never finishes.
    # 'docs/quantum_chess/quantum_chess_client.ipynb',   # uses the server, requires modification.
    'docs/hfvqe/molecular_data.ipynb',
    'docs/hfvqe/quickstart.ipynb',
    'docs/fermi_hubbard/publication_results.ipynb',
    'docs/fermi_hubbard/experiment_example.ipynb',
]


def main():
    with Pool(8) as pool:
        results = pool.map(check_notebook, NOTEBOOKS)
    print(results)


if __name__ == '__main__':
    os.makedirs('./notebook_envs', exist_ok=True)
    main()
