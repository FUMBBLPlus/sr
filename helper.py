

class InstanceRepeater(type):

  def __new__(meta, name, bases, dict_):
    dict_["_instances"] = {}
    if "__eq__" not in dict_:
      dict_["__eq__"] = (
          lambda self, other: hash(self) == hash(other)
      )
    if "__hash__" not in dict_:
      dict_["__hash__"] = (
          lambda self: hash(self._KEY)
      )
    return type.__new__(meta, name, bases, dict_)

  def __call__(cls, *args):
    if hasattr(cls, "_get_key"):
      key = cls._get_key(*args)
    else:
      key = tuple(args)
    if key in cls._instances:
      instance = cls._instances[key]
    else:
      instance = type.__call__(cls, *args)
      instance._KEY = key
      hash(instance)  # this raises TypeError if key is mutable
      cls._instances[key] = instance
    return instance


class NoInstances:

  def __new__(cls, *args, **kwargs):
    raise TypeError("class may not be instantiated")
