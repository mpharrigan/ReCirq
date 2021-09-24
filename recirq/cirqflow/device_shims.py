from typing import Optional, Sequence, AbstractSet

import cirq.work
import networkx as nx

SYC23_GRAPH = nx.from_edgelist([
    ((3, 2), (4, 2)), ((4, 1), (5, 1)), ((4, 2), (4, 1)),
    ((4, 2), (4, 3)), ((4, 2), (5, 2)), ((4, 3), (5, 3)),
    ((5, 1), (5, 0)), ((5, 1), (5, 2)), ((5, 1), (6, 1)),
    ((5, 2), (5, 3)), ((5, 2), (6, 2)), ((5, 3), (5, 4)),
    ((5, 3), (6, 3)), ((5, 4), (6, 4)), ((6, 1), (6, 2)),
    ((6, 2), (6, 3)), ((6, 2), (7, 2)), ((6, 3), (6, 4)),
    ((6, 3), (7, 3)), ((6, 4), (6, 5)), ((6, 4), (7, 4)),
    ((6, 5), (7, 5)), ((7, 2), (7, 3)), ((7, 3), (7, 4)),
    ((7, 3), (8, 3)), ((7, 4), (7, 5)), ((7, 4), (8, 4)),
    ((7, 5), (7, 6)), ((7, 5), (8, 5)), ((8, 3), (8, 4)),
    ((8, 4), (8, 5)), ((8, 4), (9, 4)),
])


class QubitsDevice(cirq.Device):
    def __init__(self, qubits: Sequence['cirq.Qid']):
        self.qubits = qubits

    def qubit_set(self) -> Optional[AbstractSet['cirq.Qid']]:
        return frozenset(self.qubits)

    def validate_circuit(self, circuit: 'cirq.Circuit') -> None:
        circuit_qubits = circuit.all_qubits()
        dev_qubits = self.qubit_set()

        bad_qubits = circuit_qubits - dev_qubits
        if bad_qubits:
            # raise ValueError(f"Circuit qubits {bad_qubits} don't exist on "
            #                  f"device with qubits {dev_qubits}.")
            pass  # TODO: care


class GraphDevice(cirq.Device):
    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.qubits = sorted(cirq.GridQubit(*rc) for rc in graph.nodes)

    def qubit_set(self) -> Optional[AbstractSet['cirq.Qid']]:
        return frozenset(self.qubits)

    def validate_circuit(self, circuit: 'cirq.Circuit') -> None:
        circuit_qubits = circuit.all_qubits()
        dev_qubits = self.qubit_set()

        bad_qubits = circuit_qubits - dev_qubits
        if bad_qubits:
            raise ValueError(f"Circuit qubits {bad_qubits} don't exist on "
                             f"device with qubits {dev_qubits}.")
