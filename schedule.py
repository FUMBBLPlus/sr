import sr

# recursive imports should get resolved in the main module:
tournament = None


class Schedule(metaclass=sr.helper.InstanceRepeater):

    def __init__(self, tournamentId):
      self._tournamentId = int(tournamentId)

    def __repr__(self):
      return f'Schedule({self._tournamentId})'

    @property
    def tournament(self):
      return tournament.Tournament(self._tournamentId)

