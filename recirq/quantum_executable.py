import uuid
from dataclasses import dataclass
from typing import Any, Union, List, Optional, Tuple
from uuid import UUID

import cirq.work
from recirq.named_topologies import ProblemTopology


@dataclass(frozen=True)
class Histogrammer:
    pass


class StructuredCircuit(cirq.Circuit):
    pass


class RunAndMeasureCircuit(cirq.Circuit):
    # TODO: what if something is structured *and* run-and-measure.
    pass


@cirq.json_serializable_dataclass(namespace='recirq', frozen=True)
class Bitstrings:
    n_repetitions: int
    measure_qubits: Optional[Tuple[cirq.Qid]] = None


@cirq.json_serializable_dataclass(namespace='recirq', frozen=True)
class Program:
    circuit: Union[cirq.FrozenCircuit, StructuredCircuit, RunAndMeasureCircuit]
    measurement: Union[Bitstrings, List[cirq.PauliSum], Histogrammer]
    param_resolver: cirq.ParamResolver = None
    info: Any = None
    problem_topology: ProblemTopology = None
    initial_state: cirq.ProductState = None
    uuid: UUID = None

    def __post_init__(self):
        if not isinstance(self.circuit, cirq.FrozenCircuit):
            # TODO: make input nicer
            raise ValueError("Need frozen circuit")

        if self.uuid is None:
            object.__setattr__(self, 'uuid', uuid.uuid4())

    def __str__(self):
        return f'Program(info={self.info})'

    def __repr__(self):
        return f'Program(info={self.info}) at {id(self)}'

    def __hash__(self):
        return hash(self.uuid)


@cirq.json_serializable_dataclass(namespace='recirq', frozen=True)
class ProgramGroup:
    info: Any
    programs: Tuple[Union[Program, 'ProgramGroup']]
    uuid: UUID = None

    def __post_init__(self):
        if self.uuid is None:
            object.__setattr__(self, 'uuid', uuid.uuid4())

        # TODO: clamp down `info` field and allow dictionaries
        # TODO: also allow lists. Just for nicer syntax.

    def __str__(self):
        return f'ProgramGroup(info={self.info})'

    def __repr__(self):
        return f'ProgramGroup(info={self.info}) at {id(self)}'

    def __hash__(self):
        return hash(self.uuid)


def get_sk_circuit(n):
    return cirq.Circuit()


def get_zz_observables(n):
    return [cirq.PauliSum()]


@dataclass
class Line(ProblemTopology):
    n: int


def example():
    executable = ProgramGroup(
        info={'name': 'qaoa-sk'},
        programs=[
            ProgramGroup(
                info={'p': 3},
                programs=[
                    Program(
                        info={'n': 2},
                        problem_topology=Line(n=2),
                        circuit=get_sk_circuit(n=2).freeze(),
                        measurement=get_zz_observables(n=2),
                    ),
                    Program(
                        info={'n': 10},
                        problem_topology=Line(n=10),
                        circuit=get_sk_circuit(n=10).freeze(),
                        measurement=get_zz_observables(n=10),
                    ),
                    # ...
                ]
            ),
            # ...
        ]
    )
