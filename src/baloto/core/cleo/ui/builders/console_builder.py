from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from baloto.core.patterns.builder import Builder


class ConsoleBuilder(Builder):
    """
    The Console-Concrete Builder classes follow the Builder interface and provide
    specific implementations of the building steps. Your program may have
    several variations of Builders, implemented differently.
    """

    def __init__(self) -> None:
        """
        A fresh builder instance should contain a blank product object, which is
        used in further assembly.
        """
        self.reset()