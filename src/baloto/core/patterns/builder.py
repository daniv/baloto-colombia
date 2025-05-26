from __future__ import annotations

from abc import ABC, abstractmethod


class Builder(ABC):

    @abstractmethod
    def build(self) -> None:
        raise NotImplementedError("This is an abstract method")


class Director:
    """
    The Director is only responsible for executing the building steps in a
    particular sequence. It is helpful when producing products according to a
    specific order or configuration. Strictly speaking, the Director class is
    optional, since the client can control builders directly.
    """

    __slots__ = ["_builder"]

    def __init__(self) -> None:
        self._builder: Builder | None = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, buildr: Builder) -> None:
        self._builder = buildr


