import dataclasses
from dataclasses import dataclass
from typing import Any, Union, List, Optional, Tuple, Hashable, Dict
from uuid import UUID, uuid4 as make_uuid4

import cirq.work
from recirq.named_topologies import ProblemTopology


@dataclass(frozen=True)
class Histogrammer:
    pass


@dataclass(frozen=True)
class FrozenCollectionOfPauliSum:
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


TParamPair = Tuple[cirq.TParamKey, cirq.TParamVal]


@cirq.json_serializable_dataclass(namespace='recirq', frozen=True)
class QuantumExecutable:
    """An executable quantum program.

    This serves a similar purpose to `cirq.Circuit` with some key differences. First, a quantum
    executable contains all the relevant context for execution including parameters as well as
    the desired number of repetitions. Second, this object is immutable. Finally, there are
    optional fields enabling a higher level of abstraction for certain aspects of the executable.

    Attributes:
        circuit: A circuit describing the quantum operations to execute.
        measurement: A description of the type of measurement. Please see the documentation for
            each possible class type for more information. The lowest level of abstraction is
            to use MeasurementGate in your circuit and specify
            `measurement=Bitstrings(n_repetitions)`.
        params: An immutable version of cirq.ParamResolver represented as a tuple of key value
            pairs.
        info: Additional metadata about this executable that is not used by the quantum runtime.
            A tuple of key value pairs where the key is a string and the value is any immutable,
            hashable value.
        problem_topology: Description of the multiqubit gate topology present in the circuit.
            If not specified, the circuit must handle compatibility with device topology.
        initial_state: How to initialize the quantum system before running `circuit`. If not
            specified, the device will be initialized into the all-zeros state.
        uuid: A unique identifer for this executable. This will be automatically generated and
            should not be set by the user unless you are reconstructing a serialized executable.
    """
    circuit: cirq.FrozenCircuit
    measurement: Union[Bitstrings, FrozenCollectionOfPauliSum, Histogrammer]
    params: Tuple[TParamPair, ...] = None
    info: Tuple[Tuple[str, Hashable], ...] = None
    problem_topology: ProblemTopology = None
    initial_state: cirq.ProductState = None
    # uuid: UUID = None

    def __init__(self,
                 circuit: cirq.AbstractCircuit,
                 measurement: Union[Bitstrings, FrozenCollectionOfPauliSum, Histogrammer],
                 params: Union[Tuple[TParamPair, ...], cirq.ParamResolverOrSimilarType] = None,
                 info: Union[Tuple[Tuple[str, Hashable], ...], Dict[str, Hashable]] = None,
                 problem_topology: ProblemTopology = None,
                 initial_state: cirq.ProductState = None,
                 uuid: UUID = None,
                 ):
        """Initialize the quantum executable.

        The actual fields in this class are immutable, but we allow more liberal input types
        which will be frozen in this __init__ method.

        Args:
            circuit: The circuit. This will be frozen before set as an attribute
            measurement: A description of the type of measurement. Please see the documentation for
                each possible class type for more information.
            params: A cirq.ParamResolverOrSimilarType which will be frozen into a tuple of
                key value pairs.
            info: Additional metadata about this executable that is not used by the quantum runtime.
                If specified as a dictioanry, this will be frozen into a tuple of key value pairs.
            problem_topology: Description of the multiqubit gate topology present in the circuit.
            initial_state: How to initialize the quantum system before running `circuit`.
            uuid: A unique identifer for this executable. This will be automatically generated and
                should not be set by the user unless you are reconstructing a serialized executable.
        """

        # We care a lot about mutability in this class. No object is truly immutable in Python,
        # but we can get pretty close by following the example of dataclass(frozen=True), which
        # deletes this class's __setattr__ magic method. To set values ever, we use
        # object.__setattr__ in this __init__ function.
        #
        # We write our own __init__ function to be able to accept a wider range of input formats
        # that can be easily converted to our native, immutable format.
        object.__setattr__(self, 'circuit', circuit.freeze())

        if not isinstance(measurement, (Bitstrings, FrozenCollectionOfPauliSum, Histogrammer)):
            raise ValueError(f"measurement should be a Bitstrings, FrozenCollectionOfPauliSum, "
                             f"or Histogrammer instance, not {measurement}.")
        object.__setattr__(self, 'measurement', measurement)

        if isinstance(params, tuple) and \
                all(isinstance(param_kv, tuple) and len(param_kv) == 2 for param_kv in params):
            frozen_params = params
        else:
            param_resolver = cirq.ParamResolver(params)
            frozen_params = tuple(param_resolver.param_dict.items())
        object.__setattr__(self, 'params', frozen_params)

        if isinstance(info, tuple) and \
                all(isinstance(info_kv, tuple) and len(info_kv) == 2 for info_kv in params):
            frozen_info = info
        else:
            frozen_info = tuple(info.items())
        object.__setattr__(self, 'info', frozen_info)

        if problem_topology is not None and not isinstance(problem_topology, ProblemTopology):
            raise ValueError(f"problem_topology should be a ProblemTopology, "
                             f"not {problem_topology}.")
        object.__setattr__(self, 'problem_topology', problem_topology)

        if initial_state is not None and not isinstance(initial_state, cirq.ProductState):
            raise ValueError(f"initial_state should be a ProductState, not {initial_state}.")
        object.__setattr__(self, 'initial_state', initial_state)

        # if uuid is None:
        #     uuid = make_uuid4()
        # if not isinstance(uuid, UUID):
        #     raise ValueError(f"uuid should be UUID, not {uuid}.")
        # object.__setattr__(self, 'uuid', uuid)
        object.__setattr__(self, '_hash', hash(dataclasses.astuple(self)))

    def info_dict(self):
        return dict(self.info)

    def __repr__(self):
        return f'QuantumExecutable(info={self.info_dict()}, uuid={self.uuid})'

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return self._hash


def _recurse_html_programgroup(pg: Union[QuantumExecutable, 'ProgramGroup'], depth=0):
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
    programs: Tuple[Union[QuantumExecutable, 'ProgramGroup']]
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
        pg: Union[QuantumExecutable, ProgramGroup],
        flat_list: List[Tuple[QuantumExecutable, InfoTuple, Tuple[ProgramGroup, ...]]],
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
                    QuantumExecutable(
                        info={'n': 2},
                        problem_topology=Line(n=2),
                        circuit=get_sk_circuit(n=2).freeze(),
                        measurement=get_zz_observables(n=2),
                    ),
                    QuantumExecutable(
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
