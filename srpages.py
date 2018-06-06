import itertools

def table(listoflist,
    align=None,
    header=None,
    header_align=None,
  ):
  if align is None:
    if listoflist:
      columns = max(len(row) for row in listoflist)
      align = 'L' * columns
  if header is not None and header_align is None:
    header_columns = len(header)
    header_align = 'C' * header_columns
  align = ''.join(s.upper() for s in align)
  header_align = ''.join(s.upper() for s in header_align)
  align_trans = {'L': '|<', 'C': '|^', 'R': '|>'}
  align_strs = [align_trans[s] for s in align]
  header_align_strs = [align_trans[s] for s in header_align]
  row_str_gen = (
      ''.join((
          ''.join(t)
          for t in
          itertools.zip_longest(align_strs, row, fillvalue='')
      ))
      for row in listoflist
  )
  if header:
    header_str = ''.join((
        ''.join(t)
        for t in
        itertools.zip_longest(
            header_align_strs,
            [f'__{a}__' for a in header],
            fillvalue=''
        )
    ))
    row_str_gen = itertools.chain([header_str], row_str_gen)
  return '\n'.join(row_str_gen)



