import asyncio
import discord

# When you decorate a method with this, the first argument must be a message
def admin_only(func):
  async def func_wrapper(self, message, *args, **kwargs):
    if message.author.name not in ["petevk", "Mugen", "RadDude"]:
      return "Sorry, you must be a Mugen admin to do that."
    return await func(self, message, *args, **kwargs)
  return func_wrapper

def private_chat_only(func):
  return _chat_type_wrapper(func, True)

def public_chat_only(func):
  return _chat_type_wrapper(func, False)

def _chat_type_wrapper(func, private_chat):
  async def func_wrapper(self, message, *args, **kwargs):
    if isinstance(message.channel, discord.channel.PrivateChannel) != private_chat:
      return "Sorry, you must be in a {} chat to do that.".format("private" if private_chat else "public")
    return await func(self, message, *args, **kwargs)
  return func_wrapper
