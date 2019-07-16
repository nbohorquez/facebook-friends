# -*- coding: utf-8 -*-

""" scrap.py Facebook spider built with scrapy """

__author__ = "Néstor Bohórquez"
__copyright__ = "Copyright 2015"
__credits__ = []
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Néstor Bohórquez"
__email__ = "tca7410nb@gmail.com"
__status__ = "Hack"

from facebook-friends.commons import config, parse_date, UnrecognizedDateFormatError
from facebook-friends.orm import FacebookUser, FacebookCity

from scrapy import FormRequest, log, Request, signals, Spider
from scrapy.xlib.pydispatch import dispatcher

from urlparse import urlparse, parse_qs

class FacebookSpider(Spider):
  name = "facebook.com"

  path_me = config.get('facebook.me', 'path')
  path_profile = config.get('facebook.paths', 'profile')
  path_login = config.get('facebook.paths', 'login')

  query_info = config.get('facebook.queries', 'info')
  query_friends = config.get('facebook.queries', 'friends')
  query_id = config.get('facebook.queries', 'id')

  base_url = config.get('facebook', 'url')
  login_url = base_url + path_login

  max_depth = config.get('scrapping', 'max_depth')

  allowed_domains = ["m.facebook.com"]
  start_urls = config.get('scrapping', 'start_urls').split(',')

  def __init__(self):
    self.logging_out = False
    self.logout_url = None
    dispatcher.connect(self.logout, signals.spider_idle)

  @staticmethod
  def profile_url(id=None):
    url = FacebookSpider.base_url
    if id[1:].isdigit():
      url += FacebookSpider.path_profile + '?' \
        + FacebookSpider.query_id + id[1:] + '&'
    else:
      url += id + '?'
    return url

  @staticmethod
  def friends_url(id=None):
    return FacebookSpider.profile_url(id) + FacebookSpider.query_friends

  @staticmethod
  def info_url(id=None):
    return FacebookSpider.profile_url(id) + FacebookSpider.query_info

  @staticmethod
  def id_from_url(url=None):
    parsed_url = urlparse(url)
    id = parsed_url.path \
    if parsed_url.path != FacebookSpider.path_profile \
    else '/' + parse_qs(parsed_url.query).get('id')[0]
    return id

  def start_requests(self):
    return [ Request(url=FacebookSpider.login_url, callback=self.login) ]

  def login(self, response):
    request = FormRequest.from_response(
      response,
      formxpath="//form[@id='login_form']",
      formdata={
        'email': config.get('facebook.me', 'email'), 
        'pass': config.get('facebook.me', 'password')
      },
      callback=self.after_login
    )

    return request

  def after_login(self, response):
    if "Tu contraseña es incorrecta" in response.body:
      self.log("Login failed", level=log.ERROR)
      return
    else:
      self.log("We are in!", level=log.DEBUG)
      self.logout_url = FacebookSpider.base_url
      self.logout_url += response.xpath("//a[contains(text(), 'Salir')]/@href")\
        .extract()[0]
      for url in FacebookSpider.start_urls:
        yield Request(url)

  def parse(self, response):
    user = FacebookUser()

    # Get the ID
    user['id'] = FacebookSpider.id_from_url(response.url).decode('utf-8')

    # Get the name
    try:
      user['name'] = response.xpath('//title/text()').extract()[0]
      root = response\
        .xpath("(//div[@id='root' and descendant::div[@id='contact-info']])[1]")
    except IndexError:
      self.log("Impossible to determine name of user. Skipping", log.CRITICAL)
      return

    # Get the picture
    user['image_urls'] = []
    if 'anabel' in user['name'].lower():
      try:
        picture_url = root.xpath("//img[parent::a[contains(@href, 'photo.php')]]/@src")
        user['image_urls'].append(picture_url.extract()[0])
      except IndexError:
        pass

    living_info = root.xpath("div/div[@id='living']")

    # Get location
    location_link = living_info\
      .xpath(
        "//a[ancestor::div[@title='Ciudad actual'] and contains(@href, '{0}')]"\
        .format(FacebookSpider.path_profile)
      )
    try:
      location_url = urlparse(location_link.xpath("@href").extract()[0])
      location = FacebookCity()
      location['id'] = '/' + parse_qs(location_url.query).get('id')[0]
      location['name'] = location_link.xpath("text()").extract()[0]
      user['location_id'] = location['id']
      yield location
    except IndexError:
      user['location_id'] = None

    # Get birthplace
    birthplace_link = living_info\
      .xpath(
        "//a[ancestor::div[@title='Ciudad de origen'] and contains(@href, '{0}')]"\
        .format(FacebookSpider.path_profile)
      )
    try:
      birthplace_url = urlparse(birthplace_link.xpath("@href").extract()[0])
      birthplace = FacebookCity()
      birthplace['id'] = '/' + parse_qs(birthplace_url.query).get('id')[0]
      birthplace['name'] = birthplace_link.xpath("text()").extract()[0] 
      user['birthplace_id'] = birthplace['id']
      yield birthplace
    except IndexError:
      user['birthplace_id'] = None

    basic_info = root.xpath("div/div[@id='basic-info']")

    # Get sex
    try:
      sex = basic_info\
        .xpath("//tr[ancestor::div[@title='Sexo']]/td[2]/div/text()")\
        .extract()[0]
      if sex == 'Hombre':
        sex = u'H'
      elif sex == 'Mujer':
        sex = u'M'
      else:
        sex = u'?'
      user['sex'] = sex
    except IndexError:
      user['sex'] = u'?'

    # Get birthdate
    try:
      birthdate = basic_info\
        .xpath("//tr[ancestor::div[@title='Fecha de nacimiento']]/td[2]/div/text()")\
        .extract()[0]
      user['birthdate'] = parse_date(birthdate)
    except (UnrecognizedDateFormatError, IndexError):
      user['birthdate'] = None

    # Get friends URL
    self.friends_url = FacebookSpider.friends_url(user['id'])
    user['friends'] = []

    # Set exploration depth level
    try:
        level = int(FacebookSpider.max_depth)\
        if not 'level' in response.meta\
        else response.meta['level']
    except:
      raise Exception("Could not determine the desired exploration depth level")

    # Check if we continue going down the tree or not
    if level == 0:
      yield user
    else:
      request = Request(url=self.friends_url, callback=self.parse_friends)
      request.meta['user'] = user
      request.meta['level'] = level - 1
      yield request

  def parse_friends(self, response):
    user = response.meta['user']
    level = response.meta['level']

    friends = response.xpath("//a[contains(@href, 'fref=fr_tab')]/@href")
    for f in friends:
      user['friends'].append(FacebookSpider.id_from_url(f.extract()))

    try:
      self.friends_url = response.xpath("//div[@id='m_more_friends']/a/@href").extract()[0]
      request = Request(
        url=FacebookSpider.base_url + self.friends_url, 
        callback=self.parse_friends
      )
      request.meta['user'] = user
      request.meta['level'] = level 
      yield request
    except IndexError:
      for f in user['friends']:
        request = Request(url=FacebookSpider.info_url(f))
        request.meta['level'] = level
        yield request

      yield user

  def logout(self, spider):
    if self.logging_out == True:
      return

    if self.logout_url is not None:
      request = Request(url=self.logout_url, callback=self.after_logout)
      self.logging_out = True
      self.crawler.engine.crawl(request, spider)

  def after_logout(self, response):
    self.log("Logged out", log.DEBUG)
