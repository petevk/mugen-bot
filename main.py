import asyncio
import discord
import logging
import sys
import yaml
from MessageHandlers import WaiverWire
from waiver_redis import WaiverRedis

with open("config.yml") as file:
  config = yaml.load(file, Loader=yaml.Loader)

client = discord.Client()
waiver_redis = WaiverRedis(host='localhost', port=6379, db=0)

waiver_wire_handler = WaiverWire(client, waiver_redis)

ALL_HANDLERS = [ waiver_wire_handler ]

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

if __name__ == "__main__":
  setup_logging(config["log_file"])
  client.run(config["bot_token"])
