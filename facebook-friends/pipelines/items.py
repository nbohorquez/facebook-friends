# -*- coding: utf-8 -*-

import sys

from facebook-friends.orm import City, friendship, initialize as initialize_db, Session, User

from scrapy.exceptions import DropItem

class ItemsPipeline(object):
  """Livingsocial pipeline for storing scraped items in the database"""
  def __init__(self):
    """
    Initializes database connection and sessionmaker.
    Creates deals table.
    """
    initialize_db()
    self.ids_seen = set()

  def process_item(self, item, spider):
    """
    Save deals in the database.
    This method is called for every item pipeline component.
    """
    if item['id'] in self.ids_seen:
      raise DropItem("Duplicate item found: {0}".format(item))
    else:
      self.ids_seen.add(item['id'])

    session = Session()

    if 'sex' in item:
      friends = item.pop('friends')
      for friend in friends:
        try:
          session.execute(friendship.insert(), params={"friend_a_id": item['id'], "friend_b_id": friend})
          session.commit()
        except:
          session.rollback()
          continue
      item.pop('image_urls')
      pictures = item.pop('images')
      if pictures:
        item['picture'] = pictures[0]['path']
      data = User(**item)
    else:
      data = City(**item)

    try:
      session.add(data)
      session.commit()
    except:
      session.rollback()
      raise Exception(
        "[ERROR]: {0} - {1}".format(sys.exc_info()[0], sys.exc_info()[1])
      )
    finally:
      session.close()

    return item
