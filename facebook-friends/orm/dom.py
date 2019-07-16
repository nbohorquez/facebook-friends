# -*- coding: utf-8 -*-

from scrapy import Item, Field

class FacebookUser(Item):
  id = Field()
  name = Field()
  picture = Field()
  location_id = Field()
  birthplace_id = Field()
  sex = Field()
  birthdate = Field()
  # Only for scrapy
  image_urls = Field()
  images = Field()
  friends = Field()

class FacebookCity(Item):
  id = Field()
  name = Field()
