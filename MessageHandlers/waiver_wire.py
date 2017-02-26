import discord
import asyncio
import requests
import redis
from distutils import util
from message_handler import MessageHandler
from utils import admin_only

class WaiverWire(MessageHandler):
  def __init__(self, client):
    self.client = client
    self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
    self.players = get_all_players()

  def match(self, message):
    return message.content.startswith("/waiver")


  async def handle(self, message):
    response = "Hmm... I couldn't understand your command. If you want the help method, type `/waiver help`"
    command = message.content[8:]

    if command.startswith("help"):
      response = HELP_MESSAGE
    elif command.startswith("admin help"):
      response = ADMIN_HELP_MESSAGE
    elif command.startswith("show player"):
      response = format_players(self.players)
    elif command.startswith("add"):
      response = await self.add_player(command[4:], message)
    elif command == "show":
      response = format_waiver_list(self.get_waivers(message.author))
    elif command.startswith("delete"):
      response = await self.delete_player_waivers(message)
    elif command.startswith("show order"):
      response = format_waiver_order(self.get_waiver_order())
    elif command.startswith("set order"):
      response = await self.set_waiver_order(message)
    elif command.startswith("reset"):
      response = await self.reset_waivers(message)
    elif command.startswith("calculate"):
      response = await self.calculate_waivers(message)

    if response:
      await self.client.send_message(message.channel, response)

  async def add_player(self, player, message):
    try:
      player_index = [p.lower() for p in self.players].index(player.lower())
    except:
      return CANNOT_FIND_PLAYER_MESSAGE.format(player)
    actual_player = self.players[player_index]
    current_waivers = self.get_waivers(message.author)

    if actual_player in current_waivers:
      return "You already requested `{}`, dummy.".format(actual_player)

    response = "Adding `{}`.".format(actual_player)
    if not current_waivers:
      await self.client.send_message(message.channel, response)
      self.set_waivers(message.author, [actual_player])
    else:
      formatted_waiver_list = format_waiver_list(current_waivers)
      response += WAIVER_SHUFFLE_ORDER_MESSAGE + formatted_waiver_list
      await self.client.send_message(message.channel, response)
      msg_order = await self.client.wait_for_message(author=message.author, timeout=30, check=valid_order_message)

      if not msg_order:
        response = "You never responded what order you wanted `{}`. Inserting at the end...".format(actual_player)
        await self.client.send_message(message.channel, response)
        order = -1
      else:
        order = min(len(current_waivers) - 1, parse_order(msg_order.content))

      if order < 0:
        current_waivers.append(actual_player)
      else:
        current_waivers.insert(order, actual_player)
      self.set_waivers(message.author, current_waivers)
      await self.client.send_message(message.channel, "Done. Type `/waiver show` to see the updated list.")

  async def delete_player_waivers(self, message):
    if not self.get_waivers(message.author):
      return "You don't have any waivers to delete!"
    await self.client.send_message(message.channel, "Are you sure you want to delete all of your waivers?")
    msg_confirm = await self.client.wait_for_message(author=message.author, timeout=30, check=valid_boolean)
    if not msg_confirm:
      return "You didn't tell me if you wanted to delete the waivers. Aborting..."
    if util.strtobool(msg_confirm.content):
      self.redis.hdel("waivers", message.author.name)
      return "Deleted all waivers."
    return "Alright, I won't delete anything."

  def get_waivers(self, author):
    result = self.redis.hget("waivers", author.name)
    return result.decode().split(":") if result else []

  def set_waivers(self, author, waivers):
    value = ":".join(waivers)
    self.redis.hmset("waivers", { author.name: value })

  def get_waiver_order(self):
    order = self.redis.lrange("waiverOrder", 0, -1)
    return [s.decode() for s in order]

  @admin_only
  async def set_waiver_order(self, message):
    raw_order =  message.content[18:]
    raw_user_ids = list(filter(None, raw_order.split(" ")))
    raw_user_ids = [user_id[3:-1] if user_id[2] == "!" else user_id[2:-1] for user_id in raw_user_ids]
    if len(raw_user_ids) != 8:
      return "Whoops, you didn't give me enough names. There should be 8."
    id_to_name = { u.id: u.name for u in self.client.get_all_members()}
    waiver_order = [id_to_name[user_id] for user_id in raw_user_ids]
    self.redis.delete("waiverOrder")
    self.redis.rpush("waiverOrder", *waiver_order)
    return format_waiver_order(self.get_waiver_order())

  @admin_only
  async def reset_waivers(self, message):
    await self.client.send_message(message.channel, "Are you sure you want to reset all the waivers?")
    msg_confirm = await self.client.wait_for_message(author=message.author, timeout=30, check=valid_boolean)
    if not msg_confirm:
      return "You didn't tell me if you wanted to delete the waivers. Aborting..."
    if util.strtobool(msg_confirm.content):
      self.redis.delete("waivers")
      return "All waivers are reset."
    return "Alright, I won't delete anything."

  @admin_only
  async def calculate_waivers(self, message):
    all_waivers = self.get_all_waivers()
    order = self.get_waiver_order()
    waivers = { name.decode(): picks.decode().split(":") for name, picks in all_waivers.items() }
    taken_players = {}
    while any(waivers.values()):
      for order_index in range(len(order)):
        name = order[order_index]
        if name in waivers and waivers[name]:
          pick = waivers[name].pop(0)
          while pick in taken_players and waivers[name]:
            pick = waivers[name].pop(0)
          if pick not in taken_players:
            taken_players[pick] = name
    results = "\n".join(["  `{}`: {}".format(player, name) for player, name in taken_players.items()])
    if not results:
      return "Nobody did waivers this week :cry:"
    return "Waiver results:\n\n{}".format(results)

  def get_all_waivers(self):
    return self.redis.hgetall("waivers")

HELP_MESSAGE = """
Welcome to the FantasyLCS waiver wire! Here are the commands you can do:
  `/waiver add playername` -- Add a waiver request for that player.
  `/waiver show` -- List your current waiver requests (and order).
  `/waiver delete` -- Remove all your current waiver requests.
  `/waiver show players` -- Show all LCS players that I know about.
  `/waiver show order` -- Show the current waiver order.
"""

ADMIN_HELP_MESSAGE = """
In addition to the regular help menu, here's the admin commands:
  `/waiver reset` -- Delete all waiver requests.
  `/waiver calculate` -- Calculate who gets who.
  `/waiver set order <names>` -- Change the waiver order to the list of names.
"""

CANNOT_FIND_PLAYER_MESSAGE = """
I'm sorry, I can't find the player `{}`. Perhaps the player is mispelled (use `/waiver show players` to find the correct spelling) or I don't know about this player yet.
"""

WAIVER_SHUFFLE_ORDER_MESSAGE = """

I see you have at least one waiver already. Please let me know what position you want to put the player.
Valid responses: Number position (`1` or `3`), English positions (`first`, `second`, `third`, `last`)
"""

WAIVER_LIST_MESSAGE = """
Here's your current waiver order:

{}
"""

def get_all_players():
  response = requests.get("http://fantasy.na.lolesports.com/en-US/api/season/14")
  players = sorted([d["name"] for d in response.json()["proPlayers"]], key=str.lower)
  teams = sorted([d["name"] for d in response.json()["proTeams"]], key=str.lower)
  return players + teams

def format_players(players):
  formatted_players = ", ".join(["`{}`".format(s) for s in players])
  return "Here are the players that I know about:\n\n{}".format(formatted_players)

def format_waiver_list(waivers):
  waiver_list = "\n".join(["  {}. `{}`".format(i + 1, p) for i, p in enumerate(waivers)])
  return WAIVER_LIST_MESSAGE.format(waiver_list) if waiver_list else "You haven't requested any waivers yet."

def format_waiver_order(order):
  order_list = "\n".join(["  {}. {}".format(i + 1, p) for i, p in enumerate(order)])
  return "Here's the latest waiver order (if this is outdated, ask a Mugen admin to update it):\n\n{}".format(order_list)

VALID_ORDER_MAPPINGS = {"first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4, "sixth": 5, "last": -1, "end": -1}

def valid_order_message(message):
  valid_messages = VALID_ORDER_MAPPINGS.keys()
  return message.content.lower() in valid_messages or is_int(message.content)

def parse_order(message):
  if message in VALID_ORDER_MAPPINGS.keys():
    return VALID_ORDER_MAPPINGS[message]
  order = int(message) - 1
  return order if order >= 0 else 0

def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def valid_boolean(message):
  try:
    util.strtobool(message.content)
    return True
  except ValueError:
    return False
