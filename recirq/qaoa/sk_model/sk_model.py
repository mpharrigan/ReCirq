# Copyright 2022 Google
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools
from dataclasses import dataclass
from typing import List, Tuple, Iterable

import networkx as nx
import numpy as np

import cirq
from cirq.protocols import dataclass_json_dict
from cirq_google.workflow import QuantumExecutable, BitstringsMeasurement, QuantumExecutableGroup, \
    ExecutableSpec
from recirq.qaoa.classical_angle_optimization import optimize_instance_interp_heuristic
from recirq.qaoa.gates_and_compilation import measure_with_final_permutation
from recirq.qaoa.problem_circuits import get_routed_sk_model_circuit


@dataclass(frozen=True)
class SKModelQAOASpec(ExecutableSpec):
    n_nodes: int
    all_to_all_couplings: Tuple[int, ...]
    p_depth: int
    n_repetitions: int
    executable_family: str = 'recirq.qaoa.sk_model'

    def __post_init__(self):
        object.__setattr__(self, 'all_to_all_couplings', tuple(self.all_to_all_couplings))

    def get_graph(self):
        if not len(self.all_to_all_couplings) == self.n_nodes * (self.n_nodes - 1) / 2:
            raise ValueError("Number of couplings does not match the number of nodes.")

        g = nx.Graph()
        u = 0
        v = 1
        for coupling in self.all_to_all_couplings:
            g.add_edge(u, v, weight=coupling)

            v += 1
            if v >= self.n_nodes:
                u += 1
                v = u + 1
        return g

    @classmethod
    def get_all_to_all_couplings_from_graph(cls, graph: nx.Graph):
        n = graph.number_of_nodes()
        # get the correct order

    @classmethod
    def _json_namespace_(cls):
        return 'recirq.qaoa'

    def _json_dict_(self):
        return dataclass_json_dict(self, namespace=self._json_namespace_())


def get_all_sk_model_qaoa_specs(
        *, n_instances: int = 10, n_repetitions: int = 10_000,
        min_size: int = 2, max_size: int = 8,
        size_step: int = 1,
        p_depths: Iterable[int] = None,
        seed: int = 52,
) -> List[SKModelQAOASpec]:
    """Return a collection of quantum executables for various parameter settings of the
    SK Model qaoa benchmark.

    Args:
        n_instances: The number of random instances to make per setting
        n_repetitions: The number of circuit repetitions to use for measuring the return
            probability.
        min_side_length, max_side_length, side_length_step: generate a range of
            problem sizes with number of nodes in this closed range (ie including max_size).
        p_depths: The list of number of QAOA (Problem, Driver) unitary repetitions. This
            hyperparameter is called "p" in the literature.
    """
    n_range = range(min_size, max_size + 1, size_step)

    if p_depths is None:
        p_depths = np.arange(1, 5 + 1, 1)

    rs = np.random.RandomState(seed)

    return [
        SKModelQAOASpec(
            n_nodes=n,
            all_to_all_couplings=tuple(rs.choice([-1, 1], size=int(n * (n - 1) / 2))),
            p_depth=p_depth,
            n_repetitions=n_repetitions,
        )
        for n, p_depth, instance_i in itertools.product(
            n_range, p_depths, range(n_instances))
    ]


def sk_model_qaoa_spec_to_exe(
        spec: SKModelQAOASpec,
) -> QuantumExecutable:
    """Create a full `QuantumExecutable` from a given `SKModelQAOASpec`

    Args:
        spec: The spec
        rs: A random state. The ExecutableSpec only specifies an `instance_i` and this function
            is responsible for generating a pseudo-random problem for each `instance_i`. Therefore,
            some care should be taken when using this function to share a `RandomState` among
            all calls to this function.

    Returns:
        a QuantumExecutable corresponding to the input specification.
    """

    n = spec.n_nodes
    graph = spec.get_graph()
    param_guess = [
        np.arccos(np.sqrt((1 + np.sqrt((n - 2) / (n - 1))) / 2)),
        -np.pi / 8
    ]

    # Returns a list starting with p = 1, so index is spec.p_depth - 1
    optima = optimize_instance_interp_heuristic(
        graph=graph,
        # To optimize for a given p_depth, we also find the optima for lower p values.
        # You could cache these instead of re-finding for each executable, to be done later
        # as necessary.
        p_max=spec.p_depth,
        param_guess_at_p1=param_guess,
        verbose=True,
    )
    # The above returns a list, but since we asked for p_max = spec.p_depth,
    # we always want the last one.
    optimum = optima[-1]
    assert optimum.p == spec.p_depth

    qubits = cirq.LineQubit.range(n)
    circuit = get_routed_sk_model_circuit(
        graph, qubits, optimum.gammas, optimum.betas, keep_zzswap_as_one_op=False)

    if all(isinstance(op.gate, cirq.QubitPermutationGate) for op in circuit[-1]):
        circuit = circuit[:-1]

    circuit += cirq.measure(*qubits, key='z')

    return QuantumExecutable(
        spec=spec,
        problem_topology=cirq.LineTopology(n),
        circuit=circuit,
        measurement=BitstringsMeasurement(spec.n_repetitions)
    )


def get_all_sk_model_qaoa_executables(
        *, n_instances: int = 10, n_repetitions: int = 10_000,
        min_size: int = 2, max_size: int = 8,
        size_step: int = 1,
        p_depths: Iterable[int] = None,
        seed: int = 52,
) -> QuantumExecutableGroup:
    """Return a collection of quantum executables for various parameter settings of the tilted
    square lattice loschmidt benchmark.
    """
    return QuantumExecutableGroup([
        sk_model_qaoa_spec_to_exe(spec)
        for spec in get_all_sk_model_qaoa_specs(
            n_instances=n_instances, n_repetitions=n_repetitions, min_size=min_size,
            max_size=max_size, size_step=size_step,
            p_depths=p_depths, seed=seed
        )
    ])
