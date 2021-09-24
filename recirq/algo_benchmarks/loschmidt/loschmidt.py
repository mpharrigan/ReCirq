import dataclasses
import itertools
from dataclasses import dataclass
from typing import List

import cirq
import numpy as np
import pandas as pd
from cirq import TiltedSquareLattice
from cirq.experiments import random_rotations_between_grid_interaction_layers_circuit
from cirq.protocols import dataclass_json_dict

from recirq.cirqflow.quantum_executable import QuantumExecutable, Bitstrings, \
    ExecutableSpec
from recirq.cirqflow.quantum_runtime import QuantumRuntimeInfo, ExecutionResult


def create_tilted_square_lattice_loschmidt_echo_circuit(
        topology: TiltedSquareLattice,
        macrocycle_depth: int,
        twoq_gate: cirq.Gate = cirq.FSimGate(np.pi / 4, 0.0),
        rs: cirq.RANDOM_STATE_OR_SEED_LIKE = None,
) -> cirq.Circuit:
    """Returns a Loschmidt echo circuit using a random unitary U.

    Args:
        qubits: Qubits to use.
        cycles: Depth of random rotations in the forward & reverse unitary.
        twoq_gate: Two-qubit gate to use.
        pause: Optional duration to pause for between U and U^\dagger.
        rs: Seed for circuit generation.
    """

    # Forward (U) operations.
    exponents = np.linspace(0, 7 / 4, 8)
    single_qubit_gates = [
        cirq.PhasedXZGate(x_exponent=0.5, z_exponent=z, axis_phase_exponent=a)
        for a, z in itertools.product(exponents, repeat=2)
    ]
    qubits = sorted(topology.nodes_as_gridqubits())
    forward = random_rotations_between_grid_interaction_layers_circuit(
        # note: this function should take a topology probably.
        qubits=qubits,
        # note: in this function, `depth` refers to cycles.
        depth=4 * macrocycle_depth,
        two_qubit_op_factory=lambda a, b, _: twoq_gate.on(a, b),
        pattern=cirq.experiments.GRID_STAGGERED_PATTERN,
        single_qubit_gates=single_qubit_gates,
        seed=rs
    )

    # Reverse (U^\dagger) operations.
    reverse = cirq.inverse(forward)

    return (forward + reverse + cirq.measure(*qubits, key='z')).freeze()


def _get_all_tilted_square_lattices(min_side_length=2, max_side_length=8, side_length_step=2):
    width_heights = np.arange(min_side_length, max_side_length + 1, side_length_step)
    return [TiltedSquareLattice(width, height)
            for width, height in itertools.combinations_with_replacement(width_heights, r=2)]


@dataclass(frozen=True)
class TiltedSquareLatticeLoschmidtSpec(ExecutableSpec):
    topology: TiltedSquareLattice
    macrocycle_depth: int
    instance_i: int
    n_repetitions: int
    executable_family: str = 'recirq.otoc.loschmidt'

    def _json_dict_(self):
        return dataclass_json_dict(self, namespace='recirq.algo_benchmarks')


def get_all_tilted_square_lattice_executables_flat(
        n_instances=10, n_repetitions=1_000,
        min_side_length=2, max_side_length=8, side_length_step=2,
        seed=52, macrocycle_depths=None,
) -> List[QuantumExecutable]:  # TODO: change to executable group
    rs = np.random.RandomState(seed)
    if macrocycle_depths is None:
        macrocycle_depths = np.arange(2, 8 + 1, 2)
    topologies = _get_all_tilted_square_lattices(
        min_side_length=min_side_length,
        max_side_length=max_side_length,
        side_length_step=side_length_step,
    )

    specs = [
        TiltedSquareLatticeLoschmidtSpec(
            executable_family='recirq.otoc.loschmidt',
            topology=topology,
            macrocycle_depth=macrocycle_depth,
            instance_i=instance_i,
            n_repetitions=n_repetitions
        )
        for topology, macrocycle_depth, instance_i in itertools.product(
            topologies, macrocycle_depths, range(n_instances))
    ]

    # TODO: return executable group?
    return [
        QuantumExecutable(
            spec=spec,
            problem_topology=spec.topology,
            circuit=create_tilted_square_lattice_loschmidt_echo_circuit(
                topology=spec.topology,
                macrocycle_depth=spec.macrocycle_depth,
                rs=rs,
            ),
            measurement=Bitstrings(spec.n_repetitions)
        )
        for spec in specs
    ]


@dataclass(frozen=True)
class TiltedSquareLatticeLoschmidtData:
    # Spec
    width: int
    height: int
    n_qubits: int
    macrocycle_depth: int
    instance_i: int
    n_repetitions: int

    # Runtime info
    run_id: str

    # Result
    success_probability: float

    @classmethod
    def from_nested(
            cls,
            spec: TiltedSquareLatticeLoschmidtSpec,
            rt_info: QuantumRuntimeInfo,
            success_probability: float
    ):
        return cls(
            width=spec.topology.width,
            height=spec.topology.height,
            n_qubits=spec.topology.n_nodes,
            macrocycle_depth=spec.macrocycle_depth,
            instance_i=spec.instance_i,
            n_repetitions=spec.n_repetitions,
            run_id=rt_info.run_id,
            success_probability=success_probability,
        )

    def _json_dict_(self):
        return dataclass_json_dict(self, namespace='recirq.algo_benchmarks')


def estimate_runtime_seconds(program: QuantumExecutable):
    # TODO: move to runtime
    if not isinstance(program.measurement, Bitstrings):
        raise NotImplementedError()

    reps = program.measurement.n_repetitions
    sampling_hz = 5_000
    sampling_s = reps / sampling_hz
    overhead_s = 0.5
    return sampling_s + overhead_s


def to_ground_state_prob(result: cirq.Result) -> float:
    return np.mean(np.sum(result.measurements["z"], axis=1) == 0)


def process_results(results: ExecutionResult):
    return [
        TiltedSquareLatticeLoschmidtData.from_nested(
            spec=result.spec,
            rt_info=result.runtime_info,
            success_probability=to_ground_state_prob(result.raw_data),
        )
        for result in results.executable_results
    ]


def flat_results_to_dataframe(results: List[TiltedSquareLatticeLoschmidtData]):
    """Turn a list of flattened, processed results into a pandas dataframe for analysis/plotting."""
    return pd.DataFrame([dataclasses.asdict(res) for res in results])


def fit_all(results: List[TiltedSquareLatticeLoschmidtData]):
    df = flat_results_to_dataframe(results)
    # TODO: fill in
