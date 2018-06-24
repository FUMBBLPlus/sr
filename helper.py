

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
    key = tuple(args)
    # cls.__instances would
    dict_ = cls._instances
    if key in dict_:
      obj = dict_[key]
    else:
      obj = type.__call__(cls, *args)
      obj._KEY = key
      hash(obj)  # this raises TypeError if mutable key
      dict_[key] = obj
    return obj
