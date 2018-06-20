import srdata


def _gen_slot_rule_values(weeknr, i):
  for g, rules in srdata.data["slot"].items():
    for rule in rules:
      if weeknr in range(*rule[:2]):
        yield g, rule[i]
        break


def coach_slots(weeknr):
  return {g: n for g, n in _gen_slot_rule_values(weeknr, 2)}


def fallback_slot_group(weeknr):
  return {
      g0: g1
      for g0, g1 in _gen_slot_rule_values(weeknr, 4)
      if g1
  }


def slot_points_included(weeknr):
  return {g: b for g, b in _gen_slot_rule_values(weeknr, 5)}


def team_slots(weeknr):
  return {g: n for g, n in _gen_slot_rule_values(weeknr, 3)}
