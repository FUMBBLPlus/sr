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
  def subgen():
    nonlocal rows
    d_table = _style2dict(style)
    if width:
      d_table["width"] = width
    tablestyle = _dict2style(d_table)
    yield _otag("table", tablestyle)
    td_aligns = itertools.cycle([align])
    tr_styles_ = itertools.cycle(tr_styles)
    if header is not None:
      rows = itertools.chain([header], rows)
      td_aligns = itertools.chain([header_align], td_aligns)
      tr_styles_ = itertools.chain([header_style], tr_styles_)
    for r, row in enumerate(rows):
      d_tr = _style2dict(next(tr_styles_))
      if hasattr(row, "style"):
        d_tr.update(_style2dict(row.style))
      trstyle = _dict2style(d_tr)
      yield indent + _otag("tr", trstyle)
      align_ = next(td_aligns)
      for c, record in enumerate(row):
        f = {"C": center, "L": left, "R": right}[align_[c]]
        d_td = {}
        if r == 0 and widths is not None:
          d_td["width"] = widths[c]
        if hasattr(record, "style"):
          d_td.update(_style2dict(record.style))
        tdstyle = _dict2style(d_td)
        yield (
            2 * indent
            + f'{_otag("td", tdstyle)}{f(record)}[/td]'
        )
      yield indent + f'[/tr]'
    yield f'[/table]'
  return f'\\{N}'.join(subgen())


def url(url, name=None):
  if name is None:
    return f'[url]{url}[/url]'
  return f'[url={url}]{name}[/url]'





def _dict2style(d):
  parts = []
  for k in sorted(d, key=lambda k: (bool(d[k]), k)):
    v = str(d[k])
    if v:
      parts.append(f'{k}={v}')
    else:
      parts.append(k)
  s = " ".join(parts)
  return s


def _otag(name, style=None):
  if style:
    return f'[{name} {style}]'
  else:
    return f'[{name}]'


def _style2dict(style):
  d = {}
  for s in style.split(" "):
    s = s.strip().lower()
    k, _, v = [s2.strip() for s2 in s.partition("=")]
    d[k] = v
  return d
