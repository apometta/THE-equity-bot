#!/usr/bin/env python3

"""This file is the module responsible for handling all interactions with
the database in THE-equity-bot.  The database contains multiple tables:
1. A table of comments/posts corresponding to all seen comments:
    ID: The submission/comment ID of the post in question.  Primary key.
    PostType: A single char "P" or "C", corresponding to whether the post in
              question is a post or comment respectively.  sqlite does not
              allow data types smaller than a byte, so this is the smallest
              way to store this information.  Messages may also be stored in
              here at a future time, so "M" is supported, but should not be
              stored in here as of now.
    Request: A boolean, true if containing a request and false if not.

2. A table containing advanced data about those posts which do contain
   requests (to be implemented.)
"""

import logging
import sqlite3

class DatabaseError(Exception):
    """Exception class for handling issues with the database."""
    pass

DB_DIRNAME = "./"
DB_FILENAME = "test.db" #change for production code
DB_PATHNAME = DB_DIRNAME + DB_FILENAME

con = sqlite3.connect(DB_PATHNAME)

def create_tables():
    """Create the necessary tables if they don't exist yet.

    Returns true if they were created, false if they were not because they
    already existed.  If some other error occurs, except."""

    #For the "comments seen" table.  We don't expect to use the M value,
    #since that corresponds to a message from our inbox which will be tracked
    #separately.  However, we may comapre this table to another table with
    #requests, which will contain this.
    create_post_table_command = """
    CREATE TABLE posts(
        ID VARCHAR(16) PRIMARY KEY,
        PostType CHAR CHECK(PostType in ("P", "C", "M"))
        Request BOOLEAN
    );
    """

    try:
        cur.execute(create_post_table_command)
        con.commit()
    except sqlite3.OperationalError as e:
        if str(e).endswith("already exists"):
            #The table already exists - just ignore error and return false
            return False
        #Legitimate error with SQL


if __name__ == "__main__":
    from RedditHandler import setup_logging
    setup_logging()
