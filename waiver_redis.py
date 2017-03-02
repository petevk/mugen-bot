import requests
from redis import StrictRedis

class WaiverRedis(StrictRedis):
  FANTASY_LCS_URL = "http://fantasy.na.lolesports.com/en-US/api/season/14"
  WAIVER_KEY = "waivers"
  WAIVER_ORDER_KEY = "waiverOrder"

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def get_all_players(self):
    players_key = "players"
    if self.llen(players_key) == 0:
      # Refresh the players cache
      response = requests.get(self.FANTASY_LCS_URL)
      players = sorted([d["name"] for d in response.json()["proPlayers"]], key=str.lower)
      teams = sorted([d["name"] for d in response.json()["proTeams"]], key=str.lower)
      self.rpush(players_key, *(players + teams))
      self.expire(players_key, 3600)
    return [p.decode() for p in self.lrange(players_key, 0, -1)]

  def get_waivers(self, name = None):
    if name:
      result = self.hget(self.WAIVER_KEY, name)
      return result.decode().split(":") if result else []
    else:
      return self.hgetall(self.WAIVER_KEY)

  def set_waivers(self, name, waivers):
    value = ":".join(waivers)
    self.hmset(self.WAIVER_KEY, { name: value })

  def delete_waivers(self, name = None):
    if name:
      self.hdel(self.WAIVER_KEY, name)
    else:
      self.delete(self.WAIVER_KEY)

  def get_waiver_order(self):
    order = self.lrange(self.WAIVER_ORDER_KEY, 0, -1)
    return [s.decode() for s in order]

  def set_waiver_order(self, order):
    self.delete(self.WAIVER_ORDER_KEY)
    self.rpush(self.WAIVER_ORDER_KEY, *order)
