import cirq
import numpy as np
from cirq import TiltedSquareLattice

from recirq.cirqflow.quantum_runtime import SYC23_GRAPH
from recirq.cirqflow.qubit_placement import NaiveQubitPlacer, GraphDevice, RandomDevicePlacer


def _get_random_circuit(qubits, n_moments=10, op_density=0.8, random_state=52):
    return cirq.testing.random_circuit(qubits, n_moments=n_moments, op_density=op_density,
                                       random_state=random_state) + cirq.measure(*qubits, key='z')


def test_naive_qubit_placer():
    p = NaiveQubitPlacer()
    qubits = cirq.LineQubit.range(10)
    circuit = _get_random_circuit(qubits=qubits)
    mapped_circuit, mapping = p.place_circuit(circuit, problem_topo=None)
    assert mapping == {q: q for q in cirq.LineQubit.range(10)}
    assert circuit == mapped_circuit


def test_random_device_placer():
    rs = np.random.RandomState()
    device = GraphDevice(SYC23_GRAPH)
    p = RandomDevicePlacer(device=device, rs=rs)
    topo = TiltedSquareLattice(2, 2)
    qubits = topo.nodes_as_gridqubits()
    circuit = _get_random_circuit(qubits=qubits)
    mapped_circuit, mapping = p.place_circuit(circuit, problem_topo=topo)
    for k, v in mapping.items():
        assert v in device.qubit_set()
