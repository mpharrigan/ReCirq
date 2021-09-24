# Copyright 2021 Google
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

import abc
from functools import lru_cache
from typing import Optional, AbstractSet, Dict, List, Any, Tuple

import cirq
import networkx as nx
import numpy as np
from cirq.devices.named_topologies import TiltedSquareLattice, get_placements, NamedTopology
from cirq.protocols import obj_to_dict_helper

from recirq.cirqflow.device_shims import GraphDevice


class QubitPlacer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def place_circuit(self, circuit: cirq.AbstractCircuit, problem_topo: NamedTopology) \
            -> Tuple[cirq.FrozenCircuit, Dict[Any, cirq.Qid]]:
        pass


class NaiveQubitPlacer(QubitPlacer):
    def place_circuit(self, circuit: cirq.AbstractCircuit, problem_topo: NamedTopology) \
            -> Tuple[cirq.FrozenCircuit, Dict[Any, cirq.Qid]]:
        return circuit.freeze(), {q: q for q in circuit.all_qubits()}

    def _json_dict_(self):
        return obj_to_dict_helper(self, attribute_names=[], namespace='cirq.google')


@lru_cache()
def cached_get_placements(problem_topo: TiltedSquareLattice, device: GraphDevice) -> List[Dict]:
    """Cache placements onto the specific device."""
    return get_placements(big_graph=device.graph, small_graph=problem_topo.graph)


class CouldNotPlaceError(RuntimeError):
    """Raised if a problem topology could not be placed on a device graph."""


def get_random_placement(problem_topo: TiltedSquareLattice, device: GraphDevice,
                         rs: np.random.RandomState) -> Dict:
    """Place `problem_topo` randomly onto a device."""
    placements = cached_get_placements(problem_topo, device)
    if len(placements) == 0:
        raise CouldNotPlaceError
    random_i = int(rs.random_integers(0, len(placements) - 1, size=1))
    placement = placements[random_i]
    placement_gq = {cirq.GridQubit(*k): cirq.GridQubit(*v) for k, v in placement.items()}
    return placement_gq


class RandomDevicePlacer(QubitPlacer):
    def __init__(
            self,
            device: GraphDevice,
            rs: np.random.RandomState,
    ):
        self.device = device
        self.rs = rs

    def place_circuit(self, circuit: cirq.AbstractCircuit, problem_topo: NamedTopology) -> Tuple[
        cirq.FrozenCircuit, Dict[Any, cirq.Qid]]:
        placement = get_random_placement(problem_topo, self.device, rs=self.rs)
        return circuit.unfreeze().transform_qubits(placement).freeze(), placement
