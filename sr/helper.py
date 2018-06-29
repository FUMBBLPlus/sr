

class InstanceRepeater(type):

  def __new__(meta, name, bases, dict_):
    dict_["__members__"] = {}
    if "__hash__" not in dict_:
      dict_["__hash__"] = (
          lambda self: hash(self._KEY)
      )
    if "__eq__" not in dict_:
      dict_["__eq__"] = (
          lambda self, other: hash(self) == hash(other)
      )
    for k in (
        "__lt__",
        "__le__",
        "__ne__",
        "__gt__",
        "__ge__",
    ):
      if k not in dict_:
        dict_[k] = (
            lambda self, other, k=k:
            getattr(self._KEY, k)(other._KEY)
        )
    return type.__new__(meta, name, bases, dict_)

  def __call__(cls, *args):
    if hasattr(cls, "_get_key"):
      key = cls._get_key(*args)
    else:
      key = tuple(args)
    if key in cls.__members__:
      instance = cls.__members__[key]
    else:
      instance = type.__call__(cls, *args)
      instance._KEY = key
      hash(instance)  # this raises TypeError if key is mutable
      cls.__members__[key] = instance
    return instance


class NoInstances:

  def __new__(cls, *args, **kwargs):
    raise TypeError("class may not be instantiated")
