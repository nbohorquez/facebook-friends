#!/usr/bin/env python
# -*- coding: utf-8 -*-

from facebook-friends.commons import ERR_OK, ERR_DB_INTEGRITY
from facebook-friends.orm import initialize as initialize_db, Session, Sex

from sqlalchemy.exc import IntegrityError

def main():
  initialize_db()
  session = Session()

  try:
    print "[INFO]: Trying to add constants to the database..."
    session.add_all([Sex('H'), Sex('M'), Sex('?')])
    session.commit()
    print "[INFO]: Success!"
    result = ERR_OK
  except IntegrityError:
    print "[ERROR]: Constants already exist in the database. Rolling back"
    session.rollback()
    result = ERR_DB_INTEGRITY

if __name__ == '__main__':
    main()
