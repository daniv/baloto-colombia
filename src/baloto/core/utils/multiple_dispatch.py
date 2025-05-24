from __future__ import annotations

import inspect
import types


class MultiMethod:
    """
    Represents a single multimethod.
    """

    def __init__(self, name):
        self._methods = {}
        self.__name__ = name

    def register(self, meth):
        """
        Register a new method as a multimethod
        """
        sig = inspect.signature(meth)

        # Build a type-signature from the method's annotations
        types = []
        for name, parm in sig.parameters.items():
            if name == "self":
                continue
            if parm.annotation is inspect.Parameter.empty:
                raise TypeError("Argument {} must be annotated with a type".format(name))
            if not isinstance(parm.annotation, type):
                raise TypeError("Argument {} annotation must be a type".format(name))
            if parm.default is not inspect.Parameter.empty:
                self._methods[tuple(types)] = meth
            types.append(parm.annotation)

        self._methods[tuple(types)] = meth

    def __call__(self, *args):
        raise TypeError("No matching method for types {}".format(types))

    def __get__(self, instance, cls):
        return self


class MultiDict(dict):
    """
    Special dictionary to build multimethods in a metaclass
    """

    def __setitem__(self, key, value):
        if key in self:
            # If key already exists, it must be a multimethod or callable
            current_value = self[key]
            if isinstance(current_value, MultiMethod):
                current_value.register(value)
            else:
                mvalue = MultiMethod(key)
                mvalue.register(current_value)
                mvalue.register(value)
                super().__setitem__(key, mvalue)
        else:
            super().__setitem__(key, value)


class MultipleMeta(type):
    """
    Metaclass that allows multiple dispatch of methods
    """

    def __new__(cls, clsname, bases, clsdict):
        return type.__new__(cls, clsname, bases, dict(clsdict))

    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()


import time


class Date(metaclass=MultipleMeta):
    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day

    def __init__(self):
        t = time.localtime()
        self.__init__(t.tm_year, t.tm_mon, t.tm_mday)
