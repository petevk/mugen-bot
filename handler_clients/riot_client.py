import requests

class RiotClient:
  def __init__(self, api_key):
    self.api_key = api_key

  def recent_game(self, summoner_id):
    response = requests.get(RECENT_GAME_URL.format(summoner_id = summoner_id, api_key = self.api_key))
    return response.json()

  def match_details(self, match_id):
    response = requests.get(MATCH_URL.format(match_id = match_id, api_key = self.api_key))
    return response.json() 

  def summoner_name(self, *summoner_ids):
    str_ids = [str(summoner_id) for summoner_id in summoner_ids]
    response = requests.get(SUMMONER_NAME_URL.format(summoner_ids = ",".join(str_ids), api_key = self.api_key))
    return { k: v["name"] for k, v in response.json().items() }

BUCHO_IDS = [ 34246411, 22370725, 27764534, 28581330, 34516600, 44947934, 21530011 ]
RECENT_GAME_URL = "https://na.api.pvp.net/api/lol/na/v1.3/game/by-summoner/{summoner_id}/recent?api_key={api_key}"
SUMMONER_NAME_URL = "https://na.api.pvp.net/api/lol/na/v1.4/summoner/{summoner_ids}?api_key={api_key}"
MATCH_URL = "https://na.api.pvp.net/api/lol/na/v2.2/match/{match_id}?api_key={api_key}"
