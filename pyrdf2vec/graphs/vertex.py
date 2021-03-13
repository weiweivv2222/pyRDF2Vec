from __future__ import annotations

import itertools
from typing import Any, Optional

import attr


@attr.s(eq=False, frozen=True, slots=True)
class Vertex:
    """Represents a vertex in a Knowledge Graph."""

    name: str = attr.ib(validator=attr.validators.instance_of(str))
    predicate: bool = attr.ib(
        default=False, validator=attr.validators.instance_of(bool), repr=False
    )
    vprev: Optional[Vertex] = attr.ib(default=None, repr=False)
    vnext: Optional[Vertex] = attr.ib(default=None, repr=False)

    _counter = itertools.count()
    id: int = attr.ib(
        init=False, factory=lambda: next(Vertex._counter), repr=False
    )

    def __eq__(self, other: Any) -> bool:
        """Defines behavior for the equality operator, ==.

        Args:
            other: The other vertex to test the equality.

        Returns:
            True if the hash of the vertices are equal, False otherwise.

        """
        if other is None:
            return False
        elif self.predicate:
            return (self.id, self.vprev, self.vnext, self.name) == (
                other.id,
                other.vprev,
                other.vnext,
                other.name,
            )
        return self.name == other.name

    def __hash__(self) -> int:
        """Defines behavior for when hash() is called on a vertex.

        Returns:
            The identifier and name of the vertex, as well as its previous
            and next neighbor if the vertex has a predicate. The hash of
            the name of the vertex otherwise.

        """
        if self.predicate:
            return hash((self.id, self.vprev, self.vnext, self.name))
        return hash(self.name)

    def __lt__(self, other: "Vertex") -> bool:
        """Defines behavior for the small than operator, <.

        Args:
            other: The other vertex.

        Returns:
            True if the first vertex is smaller than the second, False
            otherwise.

        """
        return self.name < other.name
