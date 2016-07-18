import random
import string


def id_generator(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def lang_resolver(lang):
  if not lang:
    return  'en_US'
  if lang=='vi':
    return 'vi_VN'
  if lang=='en':
    return 'en_US'
  return 'en_US'
