from collections import defaultdict
from hashlib import md5
from typing import Any, DefaultDict

from pyrdf2vec.graph import KnowledgeGraph, Vertex
from pyrdf2vec.walkers import RandomWalker


class WeisfeilerLehmanWalker(RandomWalker):
    """Defines the Weisfeler-Lehman walking strategy.

    Attributes:
        depth (int): The depth per entity.
        walks_per_graph (float): The maximum number of walks per entity.

    """

    def __init__(
        self, depth: int, walks_per_graph: float, wl_iterations: int = 4
    ):
        super().__init__(depth, walks_per_graph)
        self.wl_iterations = wl_iterations

    def _create_label(self, graph: KnowledgeGraph, vertex: Vertex, n: int):
        """Take labels of neighbors, sort them lexicographically and join."""
        neighbor_names = [
            self._label_map[x][n - 1] for x in graph.get_inv_neighbors(vertex)
        ]
        suffix = "-".join(sorted(set(map(str, neighbor_names))))

        # TODO: Experiment with not adding the prefix
        return self._label_map[vertex][n - 1] + "-" + suffix
        # return suffix

    def _weisfeiler_lehman(self, graph: KnowledgeGraph):
        """Performs Weisfeiler-Lehman relabeling of the vertices.

        Note:
            You can create a `graph.KnowledgeGraph` object from an
            `rdflib.Graph` object by using a converter method.

        Args:
            graph: The knowledge graph.

                The graph from which the neighborhoods are extracted for the
                provided instances.

        """
        self._label_map: DefaultDict[Any, Any] = defaultdict(dict)
        self._inv_label_map: DefaultDict[Any, Any] = defaultdict(dict)

        for v in graph._vertices:
            self._label_map[v][0] = v.name
            self._inv_label_map[v.name][0] = v

        for n in range(1, self.wl_iterations + 1):
            for vertex in graph._vertices:
                # Create multi-set label
                s_n = self._create_label(graph, vertex, n)
                # Store it in our label_map
                self._label_map[vertex][n] = str(md5(s_n.encode()).digest())

        for vertex in graph._vertices:
            for key, val in self._label_map[vertex].items():
                self._inv_label_map[vertex][val] = key

    def extract(self, graph: KnowledgeGraph, instances: list) -> set:
        """Extracts walks rooted at the provided instances which are then each
        transformed into a numerical representation.

        Args:
            graph: The knowledge graph.
                The graph from which the neighborhoods are extracted for the
                provided instances.
            instances: The instances to extract the knowledge graph.

        Returns:
            The 2D matrix with its:
              number of rows equal to the number of provided instances;
              number of column equal to the embedding size.

        """
        self._weisfeiler_lehman(graph)
        canonical_walks = set()
        for instance in instances:
            walks = self.extract_random_walks(graph, Vertex(str(instance)))
            for n in range(self.wl_iterations + 1):
                for walk in walks:
                    canonical_walk = []
                    for i, hop in enumerate(walk):
                        if i == 0 or i % 2 == 1:
                            canonical_walk.append(hop.name)
                        else:
                            canonical_walk.append(self._label_map[hop][n])
                    canonical_walks.add(tuple(canonical_walk))
        return canonical_walks
