import itertools
from typing import Optional, Sequence, Union

import matplotlib.pyplot as plt
import numpy as np

import cirq
import cirq_google
from cirq.experiments import random_rotations_between_grid_interaction_layers_circuit
from recirq.named_topologies import DiagonalRectangleTopology
from recirq.quantum_executable import ProgramGroup, Program, Bitstrings


def create_diagonal_rectangle_loschmidt_echo_circuit(
        topology: DiagonalRectangleTopology,
        macrocycle_depth: int,
        twoq_gate: cirq.Gate = cirq.FSimGate(np.pi / 4, 0.0),
        seed: cirq.RANDOM_STATE_OR_SEED_LIKE = None,
) -> cirq.Circuit:
    """Returns a Loschmidt echo circuit using a random unitary U.

    Args:
        qubits: Qubits to use.
        cycles: Depth of random rotations in the forward & reverse unitary.
        twoq_gate: Two-qubit gate to use.
        pause: Optional duration to pause for between U and U^\dagger.
        seed: Seed for circuit generation.
    """

    # Forward (U) operations.
    exponents = np.linspace(0, 7 / 4, 8)
    single_qubit_gates = [
        cirq.PhasedXZGate(x_exponent=0.5, z_exponent=z, axis_phase_exponent=a)
        for a, z in itertools.product(exponents, repeat=2)
    ]
    forward = random_rotations_between_grid_interaction_layers_circuit(
        # note: this function should take a topology probably.
        qubits=topology.qubits(),
        # note: in this function, `depth` refers to cycles.
        depth=4 * macrocycle_depth,
        two_qubit_op_factory=lambda a, b, _: twoq_gate.on(a, b),
        pattern=cirq.experiments.GRID_STAGGERED_PATTERN,
        single_qubit_gates=single_qubit_gates,
        seed=seed
    )

    # Reverse (U^\dagger) operations.
    reverse = cirq.inverse(forward)

    return (forward + reverse + cirq.measure(*sorted(topology.qubits()), key='z')).freeze()


def get_all_diagonal_rect_topologies(min_side_length=1, max_side_length=4):
    width_heights = np.arange(min_side_length, max_side_length + 1)
    return [DiagonalRectangleTopology(width, height)
            for width, height in itertools.combinations_with_replacement(width_heights, r=2)]


def get_all_diagonal_rect_executables(n_instances=10, n_repetitions=1_000, min_side_length=1,
                                      max_side_length=4):
    # TODO: configurable
    rs = np.random.RandomState(52)
    macrocycle_depths = np.arange(1, 10, 2)

    # TODO: put back to dictionaries and lists for pretty.
    return ProgramGroup(
        info=(('name', 'recirq.otoc.loschmidt'),),
        programs=tuple(
            ProgramGroup(
                info=(('topology', topo),),
                programs=tuple(
                    ProgramGroup(
                        info=(('macrocyle_depth', macrocycle_depth),),
                        programs=tuple(
                            Program(
                                info=(('instance_i', instance_i),),
                                problem_topology=topo,
                                circuit=create_diagonal_rectangle_loschmidt_echo_circuit(
                                    topology=topo,
                                    macrocycle_depth=macrocycle_depth,
                                    seed=rs),
                                measurement=Bitstrings(n_repetitions=n_repetitions),
                            )
                            for instance_i in range(n_instances)
                        )
                    )
                    for macrocycle_depth in macrocycle_depths
                )
            )
            for topo in get_all_diagonal_rect_topologies(min_side_length=min_side_length,
                                                         max_side_length=max_side_length)
        )
    )


def estimate_runtime_seconds(program: Program):
    if not isinstance(program.measurement, Bitstrings):
        raise NotImplementedError()

    reps = program.measurement.n_repetitions
    sampling_hz = 5_000
    sampling_s = reps / sampling_hz
    overhead_s = 0.5
    return sampling_s + overhead_s


def recurse_pg(pg: Union[Program, ProgramGroup], counter, depth=0):
    if isinstance(pg, ProgramGroup):
        print('  ' * depth + str(pg.info))
        print('  ' * depth + f'Has {len(pg.programs)} children')
        for child in pg.programs:
            recurse_pg(child, counter=counter, depth=depth + 1)
    else:
        print('  ' * depth + str(pg))
        counter[0] += 1
        counter[1] += estimate_runtime_seconds(pg)


def main():
    pg = get_all_diagonal_rect_executables(min_side_length=1, max_side_length=3)
    cirq.to_json_gzip(pg, 'loschmidt-small-v1.json.gz')
    counter = [0, 0]
    recurse_pg(pg, counter=counter)
    print('Number', counter[0])
    print('Minutes', counter[1] / 60)


if __name__ == '__main__':
    main()


def to_ground_state_prob(result: cirq.Result) -> float:
    return np.mean(np.sum(result.measurements["z"], axis=1) == 0)


def plot(probs, cycle_values):
    # Average data over trials.
    avg_probs = np.average(probs, axis=0)
    std_probs = np.std(probs, axis=0)

    # Plotting.
    plt.figure(figsize=(7, 5))

    step = len(cycle_values)
    stop = len(avg_probs) // step
    for i in range(stop):
        plt.errorbar(
            x=cycle_values,
            y=avg_probs[i * step: (i + 1) * step],
            yerr=std_probs[i * step: (i + 1) * step],
            capsize=5,
            lw=2,
            label=f"Qubit configuration {i}"
        )

    plt.legend()
    plt.ylabel("Survival probability")
    plt.xlabel("Cycle")
    plt.grid("on")


def fit():
    """Fit an exponential decay to the collected data."""
    from scipy.optimize import curve_fit

    def fit(cycle, a, f):
        return a * np.exp((f - 1.0) * cycle)

    for i in range(stop):
        (a, f), _ = curve_fit(
            fit,
            xdata=cycle_values,
            ydata=avg_probs[i * step: (i + 1) * step],
        )
        print(f"Error/cycle on qubit configuration {i}: {round((1 - f) * 100, 2)}%")


def old_main(processor_id='weber', cycle_values=tuple(range(0, 80 + 1, 2)),
             pause=None, nreps=20_000, trials=10):
    """Pick sets of qubits to run Loschmidt echoes on."""
    qubit_sets_indices = [
        [(4, 7), (4, 8), (5, 8), (5, 7)],
        [(0, 5), (0, 6), (1, 6), (1, 5)],
        # From the calibration, we expect this to be the worst configuration.
        [(2, 6), (2, 7), (3, 7), (3, 6)],
        [(7, 3), (7, 4), (8, 4), (8, 3)],
    ]

    # Convert indices to grid qubits.
    qubit_sets = [[cirq.GridQubit(*idx) for idx in qubit_indices]
                  for qubit_indices in qubit_sets_indices]

    probs = []

    for trial in range(trials):
        print("\r", f"Status: On trial {trial + 1} / {trials}", end="")

        # Create the batch of circuits.
        batch = [
            create_loschmidt_echo_circuit(qubits, cycles=c, pause=pause, seed=trial)
            for qubits in qubit_sets for c in cycle_values
        ]

        # Run the batch.
        engine = cirq_google.get_engine()
        results = engine.run_batch(
            programs=batch,
            processor_ids=[processor_id],
            repetitions=nreps,
            gate_set=cirq_google.SQRT_ISWAP_GATESET,
            params_list=[{}] * len(batch),
        )

        # Determine the ground state probability for each result.
        probs.append([to_ground_state_prob(res) for res in results])
