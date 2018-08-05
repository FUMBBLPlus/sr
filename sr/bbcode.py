import itertools

N = "\n"


def b(text):
  return f'[b]{str(text)}[/b]'

def center(text):
  return f'[block=center]{str(text)}[/block]'



def i(text):
  return f'[i]{str(text)}[/i]'


def left(text):
  return f'{str(text)}'


def right(text):
  return f'[block=right]{str(text)}[/block]'


def size(content, size=10):
  return f'[size={size}]{content}[/size]'


def table(
    rows,
    *,
    align=None,
    header=None,
    header_align=None,
    header_style="bg=black fg=white",
    style="blackborder border2",
    tr_styles=("bg=#e6ddc7", "bg=#d6cdb7"),
    width="100%",
    widths=None,
    indent="\t",
):
  if align is None:
    columns = max(len(row) for row in rows)
    align = 'L' * columns
  if header is not None and header_align is None:
    header_align = "C" * len(header)
  align = ''.join(s.upper() for s in align)
  if header_align:
    header_align = ''.join(s.upper() for s in header_align)
  widthstr = f'width={width}'
  def subgen():
    nonlocal rows
    yield f'[table {style} {widthstr}]'
    td_aligns = itertools.cycle([align])
    tr_styles_ = itertools.cycle(tr_styles)
    if header is not None:
      rows = itertools.chain([header], rows)
      td_aligns = itertools.chain([header_align], td_aligns)
      tr_styles_ = itertools.chain([header_style], tr_styles_)
    for r, row in enumerate(rows):
      yield indent + f'[tr {next(tr_styles_)}]'
      align_ = next(td_aligns)
      for c, record in enumerate(row):
        tdkwargs = {}
        if r == 0 and widths is not None:
          tdkwargs["width"] = widths[c]
        yield 2 * indent + td(
            record,
            align=align_[c],
            **tdkwargs
        )
      yield indent + f'[/tr]'
    yield f'[/table]'
  return f'\\{N}'.join(subgen())


def td(record, *, align="L", **kwargs):
  if hasattr(record, "tdkwargs"):
    kwargs.update("tdkwargs")
  alignf = {"C": center, "L": left, "R": right}[align]
  if kwargs:
    params = " ".join(f'{k}={v}' for k, v in kwargs.items())
    td0 = f'[td {params}]'
  else:
    td0 = "[td]"
  td1 = "[/td]"
  return td0 + alignf(record) + td1


def url(url, name=None):
  if name is None:
    return f'[url]{url}[/url]'
  return f'[url={url}]{name}[/url]'
