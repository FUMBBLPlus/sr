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




def idkey(cls):
  def _get_key(cls, id_: int):
    return int(id_)
  if not hasattr(cls, "_get_key"):
    setattr(cls, "_get_key", classmethod(_get_key))
  if not hasattr(cls, "id"):
    setattr(cls, "id", property(lambda self: self._KEY))
  if "__repr__" not in cls.__dict__:  # hasattr is always True
    setattr(cls, "__repr__",
          lambda self: f'{self.__class__.__name__}({self.id})'
    )
  return cls




def srdata(name, colnames,
      valattrmapping=None,
      valfsetmapping=None,
  ):

  valattrmapping = valattrmapping or {}
  valfsetmapping = valfsetmapping or {}

  def initdecorator(initmethod):
    @functools.wraps(initmethod)
    def wrapper(self, *args, **kwargs):
      for colname in colnames:
        if not hasattr(self, f'_{colname}'):
          setattr(self, f'_{colname}', ...)
      initmethod(self, *args, **kwargs)
    return wrapper

  def issetfactory(colname):
    def method(self):
      return (getattr(self, f'_{colname}') is not ...)
    return method

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

  def srdatafgetfactory(colname):
    def method(self):
      if self.srdata:
        return self.srdata[self.SRData.Idx[colname]]
      else:
        return ...
    return method

  def valfgetfactory(colname, valattrs=None):
    valattrs = valattrs or []
    def fget(self):
      for valattr in valattrs:
        if getattr(self, f'_{colname}') is ...:
          val = getattr(self, valattr)
          setattr(self, f'_{colname}', val)
          if val is not ...:
            return val
      else:
        if getattr(self, f'_{colname}') is ...:
          setattr(self, f'_{colname}', None)
      return getattr(self, f'_{colname}')
    return fget
  def valfsetfactory(colname, valfset=None):
    if valfset is None:
      if "Id" in colname or "Nr" in colname:
        valfset = int
      else:
        valfset = str
    def fset(self, val):
      if val is not None:
        setattr(self, f'_{colname}', valfset(val))
      else:
        setattr(self, f'_{colname}', None)
    return fset
  def valfdelfactory(colname):
    def fdel(self):
      setattr(self, f'_{colname}', ...)
    return fdel

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
    cls.__init__ = initdecorator(cls.__init__)
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
    for colname in colnames:
      a0 = f'srdata{colname}'
      if not hasattr(cls, a0):
        setattr(cls, a0, property(srdatafgetfactory(colname)))
      if not hasattr(cls, colname):
        valattrs = valattrmapping.get(colname, [a0])
        valfset = valfsetmapping.get(colname, None)
        setattr(cls, colname, property(
            valfgetfactory(colname, valattrs),
            valfsetfactory(colname, valfset),
            valfdelfactory(colname),
        ))
      a1 = f'{colname}isset'
      if not hasattr(cls, a1):
        setattr(cls, a1, property(issetfactory(colname)))
    setattr(cls, "savesrdata", classmethod(savesrdata))
    return cls
  return real_decorator
