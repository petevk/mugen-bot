import asyncio
import discord
from decorators import admin_only, private_chat_only, public_chat_only
from . import message_handler
from utils import is_int, valid_boolean, strtobool

class LeagueHandler(message_handler.MessageHandler):
  def __init__(self, client, riot_client):
    self.client = client
    self.riot_client = riot_client

  def match(self, message):
    return message.content.startswith("/league")

  async def handle(self, message):
    response = "Hmm... I couldn't understand your command. If you want the help method, type `/league help`"
    command = message.content[8:]

    if command.startswith("help"):
      response = HELP_MESSAGE
    elif command.startswith("last bucho") or command.startswith("lb"):
      response = await self.last_bucho()

    if response:
      await self.client.send_message(message.channel, response)

  async def last_bucho(self):
    # Last Bucho will find the last game that has been played by more
    # than one Bucho member, and give some info about said game.
    all_bucho_games = [self.riot_client.recent_game(summoner_id)["games"] for summoner_id in BUCHO_IDS]
    bucho_games = [game for games in all_bucho_games for game in games if multiple_buchos(game)]
    most_recent_game = min(bucho_games, key = lambda g: g["createDate"])
    summoner_ids = [player["summonerId"] for player in most_recent_game["fellowPlayers"]]
    buchos = set(summoner_ids).intersection(set(BUCHO_IDS))

    # Unfortunately, Riot doesn't let you see who is who is in each match, so we have to find
    # the stats by looking at each player's respective last games.
    for summoner_id in buchos:
      games = self.riot_client.recent_game(summoner_id)["games"]
      
      import pdb; pdb.set_trace()  # breakpoint 82ea9f54 //
      game = [game for game in games if game["gameId"] == most_recent_game["gameId"]][0]
      print(game)
    import pdb; pdb.set_trace()  # breakpoint 8eb08be2 //

    match_details = self.riot_client.match_details(most_recent_game["gameId"])

    all_participants = [participant for participant in match_details["participants"]]
    # bucho_details = [participant for participant in all_participants if participant[""]]
    import pdb; pdb.set_trace()  # breakpoint 0c8e3319 //

  # def last_match_from_summoners(self, *summoner_ids):
  #   recent_games = [self.recent_game(summoner_id) for summoner_id in summoner_ids]

  #   def more_than_one_bucho(game):
  #     player_ids = [player["summonerId"] for player in game["fellowPlayers"]]
  #     len(set(BUCHO_IDS).intersection(set(player_ids))) > 1

  #   games_with_more_than_one_bucho = filter(more_than_one_bucho, recent_games)
  #   most_recent_game = min([games[0] for games in recent_games], key = lambda g: g["createDate"])
  #   return most_recent_game

  # def last_bucho(self):
  #   last_match = self.last_match_from_summoners(self.BUCHO_IDS)
  #   fellow_player_ids = [fp["summonerId"] for fp in last_match["fellowPlayers"]]
  #   bucho_ids_in_last_match = list(set(fellow_player_ids).intersection(self.BUCHO_IDS))

  #   names = self.summoner_name(*bucho_ids_in_last_match)
BUCHO_IDS = [ 34246411, 22370725, 27764534, 28581330, 34516600, 44947934, 21530011 ]

HELP_MESSAGE = """
Here are the league commands you can do:
  `/league help` -- Show this message
  `/league last bucho` _or_ `/league lb` -- Show the last match played by a Bucho member
"""

def multiple_buchos(game):
  if "fellowPlayers" not in game:
    return False
  player_ids = [player["summonerId"] for player in game["fellowPlayers"]]
  return len(set(BUCHO_IDS).intersection(set(player_ids))) > 1
