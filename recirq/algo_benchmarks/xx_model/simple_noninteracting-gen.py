import cirq

from recirq.algo_benchmarks.xx_model.single_noninteracting import \
    get_all_single_noninteracting_xx_executables
from recirq.cirqflow.quantum_runtime import TimeAndPrint


def main():
    with TimeAndPrint('Create executables'):
        pg = get_all_single_noninteracting_xx_executables(
            min_length=5, max_length=5, length_step=1,
            n_instances=3, n_trotter_steps=20)
    with TimeAndPrint('Save gzip'):
        cirq.to_json_gzip(pg, 'single_noninteracting-small-v1.json.gz')


if __name__ == '__main__':
    main()
