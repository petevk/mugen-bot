import discord
import asyncio
import logging
import yaml
import sys
from MessageHandlers import WaiverWire
ALL_HANDLERS = [ WaiverWire ]

with open("config.yml") as file:
  config = yaml.load(file, Loader=yaml.Loader)

client = discord.Client()

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
  for handler_class in ALL_HANDLERS:
    handler = handler_class(client)
    if handler.match(message):
      await handler.handle(message)

if __name__ == "__main__":
  setup_logging(config["log_file"])
  client.run(config["bot_token"])
