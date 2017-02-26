import asyncio

# When you decorate a method with this, the first argument must be a message
def admin_only(func):
  async def func_wrapper(self, message, *args, **kwargs):
    if message.author.name not in ["petevk", "Mugen", "RadDude"]:
      return "Sorry, you must be a Mugen admin to do that."
      # self.client.send_message(message.channel, response)
      # return
    return await func(self, message, *args, **kwargs)
  return func_wrapper