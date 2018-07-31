import enum
import functools
import getpass
import inspect
import re


import sr
from . import roman


try:
  import fumbbl_session as S
except ImportError as exc:
  _S_importerror = exc
  S = None


INPUT_PROMPT = ":: "


class InstanceRepeater(type):

  def __new__(meta, name, bases, dict_):
    dict_["__members__"] = {}
    keys = set(dict_)
    for b in bases:
      keys |= set(b.__dict__)
    if "__hash__" not in keys:
      dict_["__hash__"] = (
          lambda self: hash(self._KEY)
      )
    if "__eq__" not in keys:
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
      if k not in keys:
        dict_[k] = (
            lambda self, other, k=k:
            getattr(self._KEY, k)(other._KEY)
        )
    return type.__new__(meta, name, bases, dict_)

  def __call__(cls, *args):
    #print("__call__", cls, args)
    if hasattr(cls, "_get_key"):
      key = cls._get_key(*args)
    else:
      key = tuple(args)
    #print("__call__", cls, args, "..")
    if key in cls.__members__:
      instance = cls.__members__[key]
    else:
      #print("type.__call__(cls, *args)")
      #instance = type.__call__(cls, *args)
      #print("instance = cls.__new__(cls)")
      instance = cls.__new__(cls)
      #print("object.__setattr__(instance, \"_KEY\", key)")
      object.__setattr__(instance, "_KEY", key)
      #print("hash(instance)")
      hash(instance)  # this raises TypeError if key is mutable
      instance.__init__(*args)
      cls.__members__[key] = instance
    #print("__call__", cls, args, "instance")
    return instance




class NoInstances:

  def __new__(cls, *args, **kwargs):
    raise TypeError("class may not be instantiated")



class NotLoggedIn(Exception): pass



def default_from_func(name, cbfunc, *cbargs, **cbkwargs):
  def real_decorator(func):
    argsp = inspect.getfullargspec(func)
    if name in argsp.args:
      argsi = argsp.args.index(name)
    else:
      argsi = None
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
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


# https://stackoverflow.com/a/14412901/2334951
def doublewrap(f):
  '''
  a decorator decorator, allowing the decorator to be used as:
  @decorator(with, arguments, and=kwargs)
  or
  @decorator
  '''
  @functools.wraps(f)
  def new_dec(*args, **kwargs):
    if (
        len(args) == 1
        and len(kwargs) == 0
        and callable(args[0])
    ):
      # actual decorated function
      return f(args[0])
    else:
      # decorator arguments
      return lambda realf: f(realf, *args, **kwargs)

  return new_dec


NOTYPECAST = lambda v: v

@doublewrap
def idkey(cls, attrname="id", ftypecast=int):
  def _get_key(cls, id_: ftypecast):
    return ftypecast(id_)
  if not hasattr(cls, "_get_key"):
    setattr(cls, "_get_key", classmethod(_get_key))
  if not hasattr(cls, attrname):
    setattr(cls, attrname, property(lambda self: self._KEY))
  if "__repr__" not in cls.__dict__:  # hasattr is always True
    setattr(cls, "__repr__",
        lambda self: (
            f'{self.__class__.__name__}'
            f'({getattr(self, attrname).__repr__()})'
        )
    )
  return cls


def objectreprhash(cls):
  cls.__hash__ = lambda self: hash(object.__repr__(self))
  return cls




def srdata(name, colnames,
    valattrmapping=None,
    valsettermapping=None,
    valdeletermapping=None,
):

  valattrmapping = valattrmapping or {}
  valsettermapping = valsettermapping or {}
  valdeletermapping = valdeletermapping or {}

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
        propertyattrs = [None] * 3
        valattrs = valattrmapping.get(colname, [a0])
        propertyattrs[0] = srdatavalfgetfactory(
            colname, valattrs
        )
        if valsettermapping.get(colname, True):
          propertyattrs[1] = srdatavalfsetfactory(colname)
        if valdeletermapping.get(colname, True):
          propertyattrs[2] = srdatavalfdelfactory(colname)
        setattr(cls, colname, property(*propertyattrs))
      a1 = f'{colname}isset'
      if not hasattr(cls, a1):
        setattr(cls, a1, property(issetfactory(colname)))
    if name is not None:
      setattr(cls, "savesrdata", classmethod(savesrdata))
    return cls
  return real_decorator

def srdatavalfgetfactory(colname, valattrs=None):
  valattrs = valattrs or []
  def fget(self):
    val = object.__getattribute__(self, f'_{colname}')
    for valattr in valattrs:
      if val in {..., None}:
        if callable(valattr):
          val = valattr(self)
        else:
          val = object.__getattribute__(self, valattr)
        if val not in {..., None}:
          break
    else:
      if val is ...:
        val = None
    if hasattr(self, f'_{colname}_fgetvalcast'):
      mname = f'_{colname}_fgetvalcast'
      m = object.__getattribute__(self, mname)
      val = m(val)
    elif hasattr(self, "_fgetvalcast"):
      m = object.__getattribute__(self, "_fgetvalcast")
      val = m(colname, val)
    return val
  return fget
def srdatavalfsetfactory(colname):
  def fset(self, val):
    oldval = getattr(self, colname)
    if hasattr(self, f'_{colname}_beforefset'):
      val = getattr(self, f'_{colname}_beforefset')(val)
    elif hasattr(self, "_beforefset"):
      val = getattr(self, "_beforefset")(colname, val)
    if val == oldval:
      return
    object.__setattr__(self, f'_{colname}', val)
    newval = getattr(self, colname)
    if hasattr(self, f'_{colname}_afterfset'):
      m = object.__getattribute__(self, f'_{colname}_afterfset')
      m(newval, oldval)
    elif hasattr(self, "_afterfset"):
      m = object.__getattribute__(self, "_afterfset")
      m(colname, newval, oldval)
  return fset
def srdatavalfdelfactory(colname):
  def fdel(self):
    setattr(self, f'_{colname}', ...)
  return fdel




def default_srdata_typecast(cls):
  def _cast(self, colname, val):
    if val not in {None, ...}:
      if "Id" in colname or "Nr" in colname:
        return int(val)
      else:
        return str(val)
  for name in ("_fgetvalcast", "_beforefset"):
    if not hasattr(cls, name):
      setattr(cls, name, _cast)
  return cls




class Input:

  prompt = ":: "

  def __init__(self, message="", response=None):
    self.exc = []
    self.message = message
    self.prevresponse = None
    self.response = response

  def __call__(self):
    while self.response is None:
      self.response = input(self.input_message())
      try:
        return self.process()
      except (IndexError, KeyError, ValueError) as exc:
        self.exc.append(exc)
        pass
      self.prevresponse = self.response
      self.response = None

  def input_message(self):
    message = self.message
    if self.prompt is not None:
      message += (" " if message else "") + self.prompt
    return message

  def process(self):
    return self.response.strip()


class IntegerInput(Input):

  def process(self):
    return int(Input.process(self))


class IntegersInput(Input):

  re_dividers = ","
  re_range_dividers = r'\s?[\-\-\—]\s?'
  subinputcls = IntegerInput

  def process(self):
    I0 = Input.process(self)
    I1 = re.split(self.re_dividers, I0)
    I2 = [s.strip() for s in I1 if s.strip()]
    print(I2)
    def subgen():
      for s in I2:
        s2 = re.split(self.re_range_dividers, s, 1)
        print(s2)
        if len(s2) == 2:
          s2 = [
              self.subinputcls(response=s).process()
              for s in s2
          ]
          s2[-1] += 1
          yield from range(*s2)
        else:
          yield self.subinputcls(response=s).process()
    return list(subgen())


class FumbblyearInput(IntegerInput):

  def process(self):
    try:
      val = int(super().process())
    except ValueError:
      val = roman.from_roman(Input.process(self))
    sr.time.fumbblyears()[val]  # raises KeyError if not exists
    return val


class FumbblyearsInput(IntegersInput):
  subinputcls = FumbblyearInput


class ReportNrInput(IntegerInput):

  def process(self):
    val = int(super().process())
    sr.report.reportNrs()[val]  # raises KeyError if not exists
    return val


class ReportNrsInput(IntegersInput):
  subinputcls = ReportNrInput


class OptionsInput(Input):

  case_sensitive = False
  options = {}

  def __init__(self, *args, **kwargs):
    if "options" in kwargs:
      self.options = kwargs["options"]
      del kwargs["options"]
    super().__init__(*args, **kwargs)

  def process(self):
    I = Input.process(self)
    if not self.case_sensitive:
      I = I.lower()
    return self.options[I]


class YesNoInput(OptionsInput):

  options = {
      "y": True,
      "yes": True,
      "n": False,
      "no": False,
  }


class CallerInput(OptionsInput):

  def process(self):
    f = super().process()
    return f()



def ensure_logged_in(interactive=True):
  if S is None:
    raise _S_importerror
  elif not S.logged_in():
    save_user_name, save_password = False, False
    user_name = sr.loginsettings["user_name"]
    if user_name is None and interactive:
      user_name = input(f'user name {INPUT_PROMPT}')
      save_user_name = input_yesno("should get saved (Y/N)?")
      if save_user_name:
        sr.loginsettings["user_name"] = user_name
    password = sr.loginsettings["password"]
    if password is None and interactive:
      password = getpass.getpass(f'password {INPUT_PROMPT}')
      if save_user_name:
        save_password = input_yesno("should get saved (Y/N)?")
        if save_password:
          sr.loginsettings["password"] = password
    S.log_in(user_name, password)
    if not S.logged_in():
      raise NotLoggedIn("not logged in")

@doublewrap
def must_logged_in(func, interactive=True):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    ensure_logged_in(interactive=interactive)
    return func(*args, **kwargs)
  return wrapper
