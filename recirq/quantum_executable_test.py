import dataclasses

import cirq
import numpy as np
import pytest

from recirq.quantum_executable import QuantumExecutable, ProgramGroup, Bitstrings


def _get_random_circuit(qubits, n_moments=10, op_density=0.8, random_state=52):
    return cirq.testing.random_circuit(qubits, n_moments=n_moments, op_density=op_density,
                                       random_state=random_state)


def test_executable():
    qubits = cirq.LineQubit.range(10)
    prog = QuantumExecutable(
        info={'name': 'example-program'},
        circuit=_get_random_circuit(qubits),
        measurement=Bitstrings(n_repetitions=10),
    )

    # Check args get turned into immutable fields
    assert prog.info == (
        ('name', 'example-program'),
    )
    assert isinstance(prog.circuit, cirq.FrozenCircuit)

    # Uses guid field since object is immutable
    assert hash(prog) is not None

    # But you could theoretically use the fields (it's just slower)
    assert hash(dataclasses.astuple(prog)) is not None

    prog2 = QuantumExecutable(
        info={'name': 'example-program'},
        circuit=_get_random_circuit(qubits),
        measurement=Bitstrings(n_repetitions=10),
    )
    assert prog == prog2
    assert hash(prog) == hash(prog2)

    prog3 = QuantumExecutable(
        info={'name': 'example-program'},
        circuit=_get_random_circuit(qubits),
        measurement=Bitstrings(n_repetitions=20), # note: changed n_repetitions
    )
    assert prog != prog3
    assert hash(prog) != hash(prog3)

    with pytest.raises(dataclasses.FrozenInstanceError):
        prog3.measurement.n_repetitions = 10


def test_tested():
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
                            QuantumExecutable(
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
