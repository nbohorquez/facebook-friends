# -*- coding: utf-8 -*-

import ConfigParser, datetime, locale, time

from datetime import date

CONFIG_FILE = 'config.ini'

ERR_OK = 0
ERR_DB_INTEGRITY = 1
ERR_TIMEOUT = 2
ERR_HTML_PARSING = 3

locale.setlocale(locale.LC_ALL, '')

config = ConfigParser.ConfigParser()
with open(CONFIG_FILE) as fp:
  config.readfp(fp)

class UnrecognizedDateFormatError(Exception):
  def __init__(self, message, date):
    super(UnrecognizedDateFormatError, self).__init__(message)
    self.date = date

def parse_date(date=None):
  try:
    time_st = time.strptime(date, '%d de %B de %Y')
    return datetime.date.fromtimestamp(time.mktime(time_st))
  except ValueError:
    pass

  try:
    time_st = time.strptime(date, '%d de %B')
    return datetime.date.fromtimestamp(time.mktime(time_st))
  except ValueError:
    pass

  try:
    time_st = time.strptime(date, '%Y')
    return datetime.date.fromtimestamp(time.mktime(time_st))
  except ValueError:
    pass

  raise UnrecognizedDateFormatError("Could not parse date", date)
