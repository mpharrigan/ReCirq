import abc
import dataclasses
from dataclasses import dataclass
from typing import Union, Optional, Tuple, Sequence, Iterable

import cirq.work
from cirq import NamedTopology
from cirq.protocols import dataclass_json_dict


class ExecutableSpec(metaclass=abc.ABCMeta):
    executable_family: str = NotImplemented


@dataclass(frozen=True)
class Histogrammer:
    pass


@dataclass(frozen=True)
class FrozenCollectionOfPauliSum:
    pass


@dataclass(frozen=True)
class Bitstrings:
    n_repetitions: int
    measure_qubits: Optional[Tuple[cirq.Qid]] = None

    def _json_dict_(self):
        return dataclass_json_dict(self, namespace='cirq.google')


TParamPair = Tuple[cirq.TParamKey, cirq.TParamVal]


@dataclass(frozen=True)
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
    spec: ExecutableSpec = None
    problem_topology: NamedTopology = None
    initial_state: cirq.ProductState = None

    def __init__(self,
                 circuit: cirq.AbstractCircuit,
                 measurement: Union[Bitstrings, FrozenCollectionOfPauliSum, Histogrammer],
                 params: Union[Tuple[TParamPair, ...], cirq.ParamResolverOrSimilarType] = None,
                 spec: ExecutableSpec = None,
                 problem_topology: NamedTopology = None,
                 initial_state: cirq.ProductState = None,
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
        elif isinstance(params, list) and \
                all(isinstance(param_kv, list) and len(param_kv) == 2 for param_kv in params):
            frozen_params = tuple((k, v) for k, v in params)
        else:
            param_resolver = cirq.ParamResolver(params)
            frozen_params = tuple(param_resolver.param_dict.items())
        object.__setattr__(self, 'params', frozen_params)

        if isinstance(spec, ExecutableSpec):
            # TODO: check for frozen?
            # TODO: update typing info or flatten into tuple
            frozen_spec = spec
        else:
            raise ValueError()
        object.__setattr__(self, 'spec', frozen_spec)

        if problem_topology is not None and not isinstance(problem_topology, NamedTopology):
            raise ValueError(f"problem_topology should be a NamedTopology, "
                             f"not {problem_topology}.")
        object.__setattr__(self, 'problem_topology', problem_topology)

        if initial_state is not None and not isinstance(initial_state, cirq.ProductState):
            raise ValueError(f"initial_state should be a ProductState, not {initial_state}.")
        object.__setattr__(self, 'initial_state', initial_state)

        object.__setattr__(self, '_hash', hash(dataclasses.astuple(self)))

    def __str__(self):
        return f'QuantumExecutable(spec={self.spec})'

    def __repr__(self):
        return f'QuantumExecutable(spec={self.spec}, ...)'

    def _json_dict_(self):
        return dataclass_json_dict(self, namespace='cirq.google')


@dataclass(frozen=True)
class QuantumExecutableGroup:
    executables: Tuple[QuantumExecutable, ...]

    def __init__(self,
                 executables: Sequence[QuantumExecutable],
                 ):

        if not isinstance(executables, tuple):
            executables = tuple(executables)
        object.__setattr__(self, 'executables', executables)

        object.__setattr__(self, '_hash', hash(dataclasses.astuple(self)))

    def __len__(self):
        return len(self.executables)

    def __iter__(self) -> Iterable[QuantumExecutable]:
        yield from self.executables

    def __str__(self):
        exe_str = str(self.executables[:2])
        if len(self.executables) > 2:
            exe_str += ', ...'

        return f'QuantumExecutable(executables={exe_str})'

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self._hash

    def _json_dict_(self):
        return dataclass_json_dict(self, namespace='cirq.google')
