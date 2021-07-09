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


def _recurse_html_programgroup(pg: Union[Program, 'ProgramGroup'], depth=0):
    if isinstance(pg, ProgramGroup):
        s = ' ' * depth + f'<li>Group {pg.info}<ul>\n'

        for child in pg.programs:
            s += _recurse_html_programgroup(child, depth=depth + 1)
        s += ' ' * depth + '</ul></li>\n'
        return s

    s = ' ' * depth + '<li>' + str(pg) + '</li>\n'
    return s


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

    def _repr_html_(self):
        return '<ul>\n' + _recurse_html_programgroup(self) + '</ul>\n'


InfoTuple = Tuple[Tuple[str, Any], ...]


def _recurse_flatten_programgroup(
        pg: Union[Program, ProgramGroup],
        flat_list: List[Tuple[Program, InfoTuple, Tuple[ProgramGroup, ...]]],
        info: InfoTuple,
        parents: Tuple[ProgramGroup, ...]
):
    new_info = dict(info)  # todo: dict-like access to info
    pg_info = dict(pg.info)  # todo: dict-like access to info
    for k in pg_info:
        if k in new_info:
            raise ValueError("Key already exists")
        new_info[k] = pg_info[k]
    new_info = tuple(new_info.items())

    if isinstance(pg, ProgramGroup):
        for child in pg.programs:
            _recurse_flatten_programgroup(
                child, flat_list=flat_list, info=new_info, parents=(pg,) + parents)
    else:
        flat_list.append((pg, new_info, parents))


def flatten_program_group(pg: ProgramGroup):
    flat_list = []
    _recurse_flatten_programgroup(pg, flat_list, (), ())
    return flat_list


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
