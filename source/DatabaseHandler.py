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
    HasRequest: A boolean, true if containing a request and false if not.

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

try:
    con = sqlite3.connect(DB_PATHNAME)
except sqlite3.OperationalError as e:
    raise DatabaseError(e)

def create_tables():
    """Create the necessary tables if they don't exist yet.

    Returns true if they were created, false if they were not because they
    already existed.  If some other error occurs, except."""

    cur = con.cursor()
    logger = logging.getLogger("db_logger")
    #For the "comments seen" table.  We don't expect to use the M value,
    #since that corresponds to a message from our inbox which will be tracked
    #separately.  However, we may comapre this table to another table with
    #requests, which will contain this.

    #Also note: booleans are just 1-byte numbers in sqlite.  We have to enforce
    #0 and 1 ourselves, even with the declaration.
    create_post_table_command = """
    CREATE TABLE posts(
        ID VARCHAR(16) PRIMARY KEY,
        PostType CHAR CHECK(PostType in ("P", "C", "M")),
        HasRequest BOOLEAN CHECK(HasRequest IN (0,1))
    );
    """

    try:
        cur.execute(create_post_table_command)
        con.commit()
    except sqlite3.OperationalError as e:
        if str(e).endswith("already exists"):
            #The table already exists - just ignore error and return false
            logger.debug("posts seen table already exists")
            return False
        #Legitimate error with SQL
        logger.critical("could not create database table (and not already "
                        "created)")
        raise DatabaseError("could not create database table")
    except:
        logger.critical("unexpected error when creating database table",
                        exc_info=True)
        raise DatabaseError("could not create database table")
    logger.debug("posts seen table created")
    return True

def check_post_seen(post_id):
    """Checks if the post, given an ID, is in the "already seen" database.

    Returns true if it is, false if it is not."""

    cur = con.cursor()
    logger = logging.getLogger("db_logger")
    search_id_command = "SELECT * FROM posts WHERE ID=?"
    try:
        cur.execute(search_id_command, (post_id,))
        row = cur.fetchone()
        if not row:
            logger.debug("post {} not seen in posts table".format(post_id))
            #It is not the job of this function to insert the post into the
            #database, only to check if it exists
            return False
        logger.debug("post {} seen in posts table".format(post_id))
        #check for duplicates
        row = cur.fetchone()
        if row:
            logger.warning("duplicate entry {} in posts table".format(post_id))
        return True
    except:
        logger.critical("unexpected error checking posts table", exc_info=True)
        raise DatabaseError("unexpected error checking posts table")

def insert_post(post_id, post_type, has_request):
    """Inserts an entry into the posts table.  post_id is the post ID,
    post_type is a single char of value 'P', 'C' or 'M' for posts, comments
    and messages respectively.  has_request is a boolean that is True when
    the post has a request for the bot.

    Returns nothing."""

    cur = con.cursor()
    logger = logging.getLogger("db_logger")

    #check that values are within expected boundaries
    if post_id is not str:
        logger.error("post_id not string (string conversion: {!s})"
                     .format(post_id))
        raise DatabaseError("post_id not string")
    if post_type not in ('P', 'C', 'M'):
        logger.error("invalid post_type {!s}".format(post_type))
        logger.debug("couldn't insert post with post id {}".format(post_id))
        raise DatabaseError("invalid post_type {!s}".format(post_type))

    #sqlite has no boolean datatype: we simply reinterpret the boolean as
    #either 0 or 1.  Nonetheless, the boolean type is forced here to ensure
    #that the argument is passed with the proper intent.
    if has_request is not bool:
        logger.error("has_request not a boolean")
        logger.debug("couldn't insert post with post id {}".format(post_id))
        raise DatabaseError("has_request is not a boolean")

    insert_args = (post_id, post_type, int(has_request))
    insert_id_command = "INSERT INTO posts VALUES (?, ?, ?);"
    try:
        cur.execute(insert_id_command, insert_args)
    except sqlite3.IntegrityError as e:
        #Occurrs when non-unique ID is to be inserted
        logger.error("attempted to insert previously seen id {}"
                     .format(post_id))
        raise DatabaseError("post id {} not unique".format(post_id))
    except:
        logger.critical("unexpected error checking posts table", exc_info=True)
        raise DatabaseError("unexpected error checking posts table")

if __name__ == "__main__":
    """While intended to be imported, if run as a standalone
    program, this module will run maintenance on the database and perform
    testing."""

    from RedditHandler import setup_logging
    setup_logging()
    logger = logging.getLogger("db_logger")
    create_tables()
