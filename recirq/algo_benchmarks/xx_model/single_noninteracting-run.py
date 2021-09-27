import os

import cirq

from recirq.algo_benchmarks.xx_model.single_noninteracting import SingleNoninteractingXxData, SingleNoninteractingXxSpec
from recirq.cirqflow.quantum_executable import QuantumExecutableGroup
from recirq.cirqflow.quantum_runtime import SimulatorBackend, QuantumRuntimeConfiguration, execute

assert SingleNoninteractingXxData, 'register deserializer'
assert SingleNoninteractingXxSpec, 'register deserializer'


def _get_runid(fmt='testrun-{i}', base_data_dir='.'):
    i = 1
    while True:
        run_id = fmt.format(i=i)
        if not os.path.exists(f'{base_data_dir}/{run_id}'):
            break  # found an unused run_id
        i += 1

    return run_id


def main():
    exegroup = cirq.read_json_gzip('single_noninteracting-small-v1.json.gz')
    rt_config = QuantumRuntimeConfiguration(
        backend=SimulatorBackend('rainbow-23', noise_strength=1e-3),
        run_id=_get_runid('testrun-{i}')
    )
    raw_results = execute(rt_config, exegroup)
    print(raw_results.shared_runtime_info.run_id)


if __name__ == '__main__':
    main()
