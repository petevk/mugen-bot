from distutils import util

def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def valid_boolean(message):
  try:
    strtobool(message.content)
    return True
  except ValueError:
    return False

def strtobool(s):
  return util.strtobool(s)
