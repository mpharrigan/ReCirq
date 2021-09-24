import dataclasses
import itertools
from typing import List

import cirq
import numpy as np
from cirq import TiltedSquareLattice
from cirq import dataclass_json_dict

from recirq.cirqflow.quantum_executable import ExecutableSpec, QuantumExecutable, Bitstrings, \
    QuantumExecutableGroup
from recirq.cirqflow.quantum_runtime import QuantumRuntimeConfiguration, SimulatorBackend, execute


def _get_random_circuit(qubits, n_moments=10, op_density=0.8, random_state=52):
    return cirq.testing.random_circuit(qubits, n_moments=n_moments, op_density=op_density,
                                       random_state=random_state) + cirq.measure(*qubits, key='z')


def get_all_topologies(min_side_length=1, max_side_length=3, side_length_step=1):
    width_heights = np.arange(min_side_length, max_side_length + 1, side_length_step)
    return [TiltedSquareLattice(width, height)
            for width, height in itertools.combinations_with_replacement(width_heights, r=2)]


@dataclasses.dataclass(frozen=True)
class ExampleSpec(ExecutableSpec):
    name: str
    topology: TiltedSquareLattice
    executable_family = 'recirq.algo_benchmarks.example'

    def _json_dict_(self):
        return dataclass_json_dict(self, namespace='cirq.google')


def _get_all_specs():
    return [
        ExampleSpec(
            name='example-program',
            topology=topo
        )
        for topo in get_all_topologies()
    ]


def _get_all_exes(specs: List[ExampleSpec]):
    return [
        QuantumExecutable(
            spec=spec,
            circuit=_get_random_circuit(qubits=spec.topology.nodes_as_gridqubits()),
            measurement=Bitstrings(n_repetitions=10)
        )
        for spec in specs
    ]


def test_execute(tmpdir):
    rt_config = QuantumRuntimeConfiguration(
        backend=SimulatorBackend(name='rainbow-23'),
    )

    executable_group = QuantumExecutableGroup(_get_all_exes(_get_all_specs()))
    print(len(executable_group))
    execute(rt_config, executable_group, base_data_dir=tmpdir)
