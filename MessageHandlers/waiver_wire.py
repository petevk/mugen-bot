import discord
import asyncio
from message_handler import MessageHandler

class WaiverWire(MessageHandler):
  def __init__(self, client):
    self.client = client

  def match(self, message):
    return True

  async def handle(self, message):
    await self.client.send_message(message.channel, "Calculating messages...")

  # if message.content.startswith("!test"):
  #   counter = 0
  #   tmp = await client.send_message(message.channel, "Calculating messages...")
  #   async for log in client.logs_from(message.channel, limit=100):
  #     if log.author == message.author:
  #       counter += 1

  #   await client.edit_message(tmp, "You have {} messages.".format(counter))
  # elif message.content.startswith("!sleep"):
  #   await asyncio.sleep(5)
  #   await client.send_message(message.channel, "Done sleeping")