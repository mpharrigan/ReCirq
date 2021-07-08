from typing import Optional
import networkx as nx
from matplotlib import pyplot as plt

import cirq


class ProblemTopology:
    pass


class LineTopology(ProblemTopology):
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.name = f'{self.n_qubits}q-line'
        self.graph = nx.from_edgelist([(i1, i2) for i1, i2
                                       in zip(range(self.n_qubits), range(1, self.n_qubits))])


def draw_gridlike(graph: nx.Graph, ax=None, cartesian=True, **kwargs):
    if ax is None:
        ax = plt.gca()

    if cartesian:
        pos = {n: (n[1], -n[0]) for n in graph.nodes}
    else:
        pos = {(x, y): (x + y, y - x) for x, y in graph.nodes}

    nx.draw_networkx(graph, pos=pos, ax=ax, **kwargs)
    ax.axis('equal')
    return pos


class DiagonalRectangleTopology(ProblemTopology):
    def __init__(self, width: int, height: int):
        g = nx.Graph()
        for megarow in range(height):
            for megacol in range(width):
                y = megacol + megarow
                x = megacol - megarow
                g.add_edge((x, y), (x - 1, y))
                g.add_edge((x, y), (x, y - 1))
                g.add_edge((x, y), (x + 1, y))
                g.add_edge((x, y), (x, y + 1))

        self.width = width
        self.height = height
        self.name = f'{width}-{height}-diagonal-rectangle'
        self.graph = g
        self.n_qubits = 2 * width * height + width + height + 1
        assert self.n_qubits == len(g), (self.n_qubits, len(g))

    def draw(self, ax=None, cartesian=True, **kwargs):
        return draw_gridlike(self.graph, ax=ax, cartesian=cartesian, **kwargs)

    def qubits(self):
        import cirq
        return [cirq.GridQubit(r, c) for r, c in sorted(self.graph.nodes)]

    def __repr__(self):
        return f'DiagonalRectangleTopology(width={self.width}, height={self.height})'

    def _json_dict_(self):
        # TODO: to dataclass with __post_init__?
        # TODO: should we serialize the graph?
        return cirq.obj_to_dict_helper(self, attribute_names=['width', 'height'],
                                       namespace='recirq')


def get_placements(big_graph: nx.Graph, small_graph: nx.Graph, plt=None, max_plot=20):
    matcher = nx.algorithms.isomorphism.GraphMatcher(big_graph, small_graph)

    count = 0
    dedupe = {}
    for big_to_small_map in matcher.subgraph_monomorphisms_iter():
        dedupe[frozenset(big_to_small_map.keys())] = big_to_small_map
        count += 1
    print(count)
    print(len(dedupe))

    count = 0
    small_mappeds = []
    for big_to_small_map in dedupe.values():
        count += 1
        small_to_big_map = {v: k for k, v in big_to_small_map.items()}
        small_mapped = nx.relabel_nodes(small_graph, small_to_big_map)
        small_mappeds.append(small_mapped)

        if plt is not None and count < max_plot:
            pos = {n: (n[1], -n[0]) for n in big_graph.nodes}
            nx.draw_networkx(big_graph, pos=pos, ax=plt.gca())

            pos = {n: (n[1], -n[0]) for n in small_mapped.nodes}
            nx.draw_networkx(small_mapped, pos=pos, node_color='red', edge_color='red', width=2,
                             with_labels=False)
            plt.axis('equal')
            plt.show()

    return small_mappeds
