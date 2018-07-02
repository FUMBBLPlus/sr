import enum
import functools
import inspect


import sr


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




def default_from_func(name, cbfunc, *cbargs, **cbkwargs):
  def real_decorator(func):
    argsp = inspect.getfullargspec(func)
    #print(argsp)
    if name in argsp.args:
      argsi = argsp.args.index(name)
    else:
      argsi = None
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      #print([argsi, kw, args, kwargs])
      if name in kwargs:
        if kwargs[name] is None:
            kwargs[name] = cbfunc(*cbargs, **cbkwargs)
      elif argsi is not None:
        if argsi == len(args):
          args = list(args) + [None]
        elif args:
          args = list(args)
        if args[argsi] is None:
            args[argsi] = cbfunc(*cbargs, **cbkwargs)
      return func(*args, **kwargs)
    return wrapper
  return real_decorator




def srdata(name, colnames):

  def savesrdata(cls):
    sr._data.save(cls.SRData.name)

  def srdata(self):
    srdata_row = sr.data[self.SRData.name].get(self.id)
    if srdata_row:
      return tuple(srdata_row)

  def srdataischanged(self):
    return (self.srdata != self.srnewdata)

  def srisnew(self):
    return (self.srdata is None)

  def srnewdata(self):
    attrs = tuple(self.SRData.Idx.__members__)
    return tuple(getattr(self, a) for a in attrs)

  def srnewdata_apply(self):
    sr.data[self.SRData.name][self.id] = list(self.srnewdata)

  def srdatagetter(fieldname):
    def method(self):
      if self.srdata:
        return self.srdata[self.SRData.Idx[fieldname]]
      else:
        return ...
    return method

  property_attr = {
    "srdata": (srdata,),
    "srdataischanged": (srdataischanged,),
    "srisnew": (srisnew,),
    "srnewdata": (srnewdata,),
  }
  method = {
    "srnewdata_apply": srnewdata_apply,
  }

  def real_decorator(cls):
    if not hasattr(cls, "SRData"):
      Idx = enum.IntEnum(
          "Idx",
          {n:i for i, n in enumerate(colnames)},
      )
      cls.SRData = type(
          "SRData",
          (NoInstances,),
          {"name": name, "Idx": Idx}
      )
    for pname, pattr in property_attr.items():
      if not hasattr(cls, pname):
        setattr(cls, pname, property(*pattr))
    for mname, meth in method.items():
      if not hasattr(cls, mname):
        setattr(cls, mname, meth)
    for c in colnames:
      a = f'srdata{c}'
      if not hasattr(cls, a):
        setattr(cls, a, property(srdatagetter(c)))
    setattr(cls, "savesrdata", classmethod(savesrdata))
    return cls
  return real_decorator


def srdatarecord(fieldname):
  def method(self):
    if self.srdata:
      return self.srdata[self.SRData.Idx[fieldname]]
