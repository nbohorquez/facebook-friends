#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" scrap.py Facebook spider built with selenium """

__author__ = "Néstor Bohórquez"
__copyright__ = "Copyright 2015"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Néstor Bohórquez"
__email__ = "tca7410nb@gmail.com"
__status__ = "Hack"

import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from facebook-friends.commons import (
  config, ERR_OK, ERR_DB_INTEGRITY, ERR_TIMEOUT, ERR_HTML_PARSING, 
  parse_date, UnrecognizedDateFormatError 
)
from facebook-friends.orm import City, initialize as initialize_db, Session, Sex, User

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from threading import Thread

from urlparse import urlparse, parse_qs

base_url = config.get('facebook', 'url')
path2me = config.get('facebook.me', 'path')
path2profile = config.get('facebook.paths', 'profile')
query_info = config.get('facebook.queries', 'info')
query_friends = config.get('facebook.queries', 'friends')
query_id = config.get('facebook.queries', 'id')

def authenticate(browser=None):
  email_field = browser.find_element(By.XPATH, "//input[@name='email']")
  email_field.send_keys(config.get('facebook.me', 'email'))
  pass_field = browser.find_element(By.XPATH, "//input[@name='pass']")
  pass_field.send_keys(config.get('facebook.me', 'password'))
  pass_field.submit()

  try:
    WebDriverWait(browser, 10).until(EC.title_is("Facebook"))
    print "[DEBUG]: Now on Index"
  except TimeoutException:
    print "[ERROR]: Home page did not load on time or title was not 'Facebook'"
    return ERR_TIMEOUT

  return ERR_OK

def get_living_info(session=None, root=None):
  location = {'id': None, 'name': ''}
  birthplace = {'id': None, 'name': ''}

  try:
    living = root.find_element(By.ID, "living")
  except NoSuchElementException:
    print "[ERROR]: Could not find 'living' section"
    return location, birthplace

  try:
    location_elem = living.find_element(
      By.XPATH, "//div[@title='Ciudad actual']/table/tbody/tr/td[2]/div/a"
    )
    location_url = urlparse(location_elem.get_attribute('href'))
    location['id'] = '/' + parse_qs(location_url.query).get('id')[0]
    location['name'] = location_elem.text
    add_city(session, location['id'], location['name'])
  except NoSuchElementException:
    print "[ERROR]: No information about current city"
      
  try:
    birthplace_elem = living.find_element(
      By.XPATH, "//div[@title='Ciudad de origen']/table/tbody/tr/td[2]/div/a"
    )
    birthplace_url = urlparse(birthplace_elem.get_attribute('href'))
    birthplace['id'] = '/' + parse_qs(birthplace_url.query).get('id')[0]
    birthplace['name'] = birthplace_elem.text
    add_city(session, birthplace['id'], birthplace['name'])
  except NoSuchElementException:
    print "[ERROR]: No information about birthplace"

  return location, birthplace

def get_basic_info(root=None):
  sex = u'?'
  birthdate = None

  try:
    basic_info = root.find_element(By.ID, "basic-info")
  except NoSuchElementException:
    print "[ERROR]: Could not find 'basic-info' section"
    return sex, birthdate

  try:
    sex_elem = basic_info.find_element(
      By.XPATH, "//div[@title='Sexo']/table/tbody/tr/td[2]/div"
    )
    if sex_elem.text == 'Hombre':
      sex = u'H'
    elif sex_elem.text == 'Mujer':
      sex = u'M'
    else:
      sex = u'?'
  except NoSuchElementException:
    print "[ERROR]: No information about gender"

  try:
    birthdate_elem = basic_info.find_element(
      By.XPATH, "//div[@title='Fecha de nacimiento']/table/tbody/tr/td[2]/div"
    )
    birthdate = parse_date(birthdate_elem.text)
  except NoSuchElementException:
    print "[ERROR]: No information about birthdate"
  except UnrecognizedDateFormatError as e:
    print "[ERROR]: Unrecognized date format for '{0}'".format(e.date)

  return sex, birthdate

def add_city(session=None, id=None, name=None):
  try:
    print "[INFO]: Trying to add city {0} to the database..."\
      .format(name.encode('utf-8'))
    session.add(City(id, name))
    session.commit()
    print "[INFO]: Success!"
    result = ERR_OK
  except IntegrityError:
    print "[ERROR]: City {0} already exists in the database. Rolling back"\
      .format(name.encode('utf-8'))
    session.rollback()
    result = ERR_DB_INTEGRITY
  
  return result

def add_user(session=None, browser=None, id=None):
  print "[INFO]: Trying to add user {0} to the database...".format(id)

  (ret, ), = session.query(exists().where(User.id == id))
  if (ret):
    print "[ERROR]: User {0} already exists in the database".format(id)
    return None, ERR_DB_INTEGRITY

  try:
    url = base_url
    if id[1:].isdigit():
      url += path2profile + '?' + query_id + id[1:] + '&'
    else:
      url += id + '?'
    url += query_info
    browser.get(url)
    root = WebDriverWait(browser, 20).until(
      EC.presence_of_element_located(
        (By.XPATH, "//div[@id='root' and descendant::div[@id='contact-info']]")
      )
    )
  except TimeoutException:
    print "[ERROR]: Info page did not load on time or 'root' div was not found"
    return None, ERR_HTML_PARSING

  name = browser.title
  print "[{0}](name): {1}".format(id, name.encode('utf-8'))
    
  location, birthplace = get_living_info(session, root)
  print "[{0}](location): {1}".format(id, location['name'].encode('utf-8'))
  print "[{0}](birthplace): {1}".format(id, birthplace['name'].encode('utf-8'))

  sex, birthdate = get_basic_info(root)
  print "[{0}](sex): {1}".format(id, sex.encode('utf-8'))
  print "[{0}](birthdate): {1}".format(id, birthdate)

  user = None

  try:
    user = User(id, name, location['id'], birthplace['id'], sex, birthdate)
    session.add(user)
    session.commit()
    print "[INFO]: Success!"
  except IntegrityError:
    print "[ERROR]: User {0} already exists in the database. Rolling back"\
      .format(id)
    session.rollback()
    return None, ERR_DB_INTEGRITY

  return user, ERR_OK

def list_friends(browser=None, id=None):
  try:
    url = base_url
    if id[1:].isdigit():
      url += path2profile + '?' + query_id + id[1:] + '&'
    else:
      url += id + '?'
    url += query_friends
    browser.get(url)
    WebDriverWait(browser, 20).until(EC.presence_of_element_located(
      (By.XPATH, "//h3[ancestor::div[@id='root']]")
    ))
  except TimeoutException:
    print "[ERROR]: Friends page did not load on time or h3 was not found"
    return [], ERR_HTML_PARSING

  friends = []
  
  while True:
    friends_list = browser.find_elements(
      By.XPATH, 
      "//div[@class='bn' or @class='bq' or @class='bm' or @class='bp']/a[not(@class)]"
    )
    for friend in friends_list:
      url = urlparse(friend.get_attribute("href"))
      friend_id = url.path \
      if url.path != '/profile.php' \
      else '/' + parse_qs(url.query).get('id')[0]
      friends.append(friend_id)

    try:
      more_friends_link = browser.find_element(
        By.XPATH, "//div[@id='m_more_friends']/a"
      )
      browser.get(more_friends_link.get_attribute("href"))
      WebDriverWait(browser, 10).until(EC.presence_of_element_located(
        (By.XPATH, "//h3[ancestor::div[@id='root']]")
      ))
    except NoSuchElementException:
      break
    except TimeoutException:
      break

  return friends, ERR_OK

class Scrapper(Thread):
  def __init__(self, starting_id=None, pal=None, recursivity_level=1, *args, 
               **kwargs):
    super(Scrapper, self).__init__(*args, **kwargs)
    #Thread.__init__(self)
    self.kill_yourself = False
    self.starting_id = starting_id
    self.pal = pal
    self.session = Session()
    self.browser = webdriver.Firefox()

  def add_users(self, id=None, pal=None, recursivity_level=1):
    if self.kill_yourself:
      return

    user, ret = add_user(self.session, self.browser, id)
    if ret == ERR_HTML_PARSING:
      return
    if pal != None:
      try:
        pal.friends.append(user)
        self.session.commit()
      except IntegrityError:
        self.session.rollback()

    if recursivity_level == 0:
      return

    friends, ret = list_friends(self.browser, id)

    i = 0
    N = len(friends)
    for friend in friends:
      self.add_users(friend, user, recursivity_level-1)
      print "[{0}]({1}/{2}): {3} (level = {4})"\
        .format(id, i, N, friend, recursivity_level)
      i += 1

  def run(self):
    self.browser.get(base_url)
    print "[TITLE]: {0}".format(self.browser.title)

    if authenticate(self.browser) == ERR_OK:
      self.add_users(self.starting_id, self.pal, 2)

    self.stop()

  def stop(self):
    print "[INFO]: Stopping thread {0}".format(self.name)
    self.session.close()
    logout_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Salir")
    self.browser.get(logout_link.get_attribute('href'))
    time.sleep(3)
    self.browser.quit()

scrappers = []

def main():
  initialize_db()

  global scrappers
  s = Scrapper(path2me, None, 2)
  s.daemon = True
  scrappers.append(s)

  [s.start() for s in scrappers]
  print "[INFO]: {0} scrapper(s) started".format(len(scrappers))

  time.sleep(1)

  while len(scrappers) > 0:
    try:
      # Join all threads using a timeout so it doesn't block
      [s.join(1) for s in scrappers]
      # Filter out threads which have been joined or are None
      scrappers = [s for s in scrappers if s is not None and s.isAlive()]
    except KeyboardInterrupt:
      print "[INFO]: Ctrl-C received! Sending kill to scrappers..."
      for s in scrappers:
        s.kill_yourself = True

  print "[INFO]: Scrapper(s) stopped"

if __name__ == '__main__':
  main()
