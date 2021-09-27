import dataclasses
import itertools
from dataclasses import dataclass
from typing import Sequence, Optional, List

import cirq
import numpy as np
import pandas as pd
from cirq import dataclass_json_dict, LineTopology

from recirq.cirqflow.quantum_executable import ExecutableSpec, QuantumExecutableGroup, \
    QuantumExecutable, Bitstrings
from recirq.cirqflow.quantum_runtime import QuantumRuntimeInfo, ExecutionResult

SQRT_ISWAP = cirq.ISWAP ** 0.5


def create_linear_chain_segment(
        qubits: Sequence[cirq.Qid],
        n_trotter_steps: int,
) -> cirq.Circuit:
    """Returns a linear chain circuit on one segment."""
    circuit = cirq.Circuit(cirq.X.on(qubits[len(qubits) // 2]))

    # Trotter steps.
    for step in range(n_trotter_steps):
        offset = step % 2
        circuit += cirq.Moment(
            [SQRT_ISWAP.on(a, b) for a, b in zip(qubits[offset::2],
                                                 qubits[offset + 1::2])])
    return circuit + cirq.measure(*qubits, key='z')


@dataclass(frozen=True)
class SingleNoninteractingXxSpec(ExecutableSpec):
    topology: LineTopology
    n_trotter_steps: int

    instance_i: int
    n_repetitions: int
    executable_family: str = 'recirq.algo_benchmarks.xx_model.single_noninteracting'

    def _json_dict_(self):
        return dataclass_json_dict(self, namespace='recirq.algo_benchmarks')


def _get_all_lines(min_length=5, max_length=5, length_step=2):
    return [LineTopology(l) for l in range(min_length, max_length + 1, length_step)]


def get_all_single_noninteracting_xx_executables(
        *,
        n_trotter_steps=20,
        n_instances=4, n_repetitions=20_000,
        min_length=5, max_length=5, length_step=2,

) -> QuantumExecutableGroup:
    topologies = _get_all_lines(
        min_length=min_length,
        max_length=max_length,
        length_step=length_step,
    )

    specs = [
        SingleNoninteractingXxSpec(
            topology=topology,
            n_trotter_steps=n_trotter_steps,
            instance_i=instance_i,
            n_repetitions=n_repetitions,
        )
        for topology, instance_i in itertools.product(
            topologies, range(n_instances))
    ]

    return QuantumExecutableGroup([
        QuantumExecutable(
            spec=spec,
            problem_topology=spec.topology,
            circuit=create_linear_chain_segment(
                qubits=spec.topology.nodes_as_linequbits(),
                n_trotter_steps=spec.n_trotter_steps
            ),
            measurement=Bitstrings(spec.n_repetitions)
        )
        for spec in specs
    ])


@dataclass(frozen=True)
class SingleNoninteractingXxData:
    # Spec
    n_sites: int
    n_trotter_steps: int
    instance_i: int
    n_repetitions: int

    # Runtime info
    run_id: str

    # Result
    z_densities: np.ndarray

    @classmethod
    def from_nested(
            cls,
            spec: SingleNoninteractingXxSpec,
            rt_info: QuantumRuntimeInfo,
            z_densities: np.ndarray,
    ):
        return cls(
            n_sites=spec.topology.n_nodes,
            n_trotter_steps=spec.n_trotter_steps,
            instance_i=spec.instance_i,
            n_repetitions=spec.n_repetitions,
            run_id=rt_info.run_id,
            z_densities=z_densities,
        )

    def _json_dict_(self):
        return dataclass_json_dict(self, namespace='recirq.algo_benchmarks')


def z_densities_from_measurements(
        measurements: np.ndarray,
        post_select_filling: Optional[int] = 1
) -> np.ndarray:
    """Returns density for one segment on the line, length is number of sites."""
    counts = np.sum(measurements, axis=1, dtype=int)

    if post_select_filling is not None:
        errors = np.abs(counts - post_select_filling)
        counts = measurements[errors == 0]

    return np.average(counts, axis=0)


def process_results(results: ExecutionResult, post_select_filling=1):
    return [
        SingleNoninteractingXxData.from_nested(
            spec=result.spec,
            rt_info=result.runtime_info,
            z_densities=z_densities_from_measurements(
                result.raw_data.measurements['z'],
                post_select_filling=post_select_filling)
            # ...
        )
        for result in results.executable_results
    ]


def flat_results_to_dataframe(results: List[SingleNoninteractingXxData]):
    """Turn a list of flattened, processed results into a pandas dataframe for analysis/plotting."""
    return pd.DataFrame([dataclasses.asdict(res) for res in results])
