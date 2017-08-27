import asyncio
import discord
import logging
import sys
import yaml
from message_handlers import *
from handler_clients.waiver_redis import WaiverRedis
from handler_clients.riot_client import RiotClient

with open("config.yml") as file:
  config = yaml.load(file, Loader=yaml.Loader)

client = discord.Client()

waiver_redis = WaiverRedis(host='localhost', port=6379, db=0)
waiver_wire_handler = waiver_wire.WaiverWire(client, waiver_redis)

riot_client = RiotClient(config["riot_api_key"])
league_handler = league.LeagueHandler(client, riot_client)

ALL_HANDLERS = [ waiver_wire_handler, league_handler ]

def setup_logging(filename):
  logger = logging.getLogger("discord")
  logger.setLevel(logging.DEBUG)
  handler = logging.FileHandler(filename=filename, encoding="utf-8", mode="w")
  handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
  logger.addHandler(handler)

@client.event
async def on_ready():
  print("Logged in as")
  print(client.user.name)
  print(client.user.id)
  print("------")

@client.event
async def on_message(message):
  for handler in ALL_HANDLERS:
    if handler.match(message):
      await handler.handle(message)

@client.event
async def on_member_update(before, after):
  if after.game and after.game.name == "League of Legends":
    channel = discord.utils.get(client.get_all_channels(), server__name="Mucho Bucho", name="general")
    await client.send_message(channel, "{} wants to play League!".format(after.mention))

if __name__ == "__main__":
  setup_logging(config["log_file"])
  client.run(config["bot_token"])
