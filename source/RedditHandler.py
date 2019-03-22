#!/usr/bin/env python3

"""This file, which can be treated as the "main" file, is the .py responsible
for interfacing with Reddit for THE-equity-bot.  Written by Andrew H. Pometta.
As of now, it is solely a skeleton of the project.  """

import datetime
import time
import praw
import sys
import logging

#de facto constants
PRAW_COMMENT = praw.models.reddit.comment.Comment
PRAW_SUBMISSION = praw.models.reddit.submission.Submission
CFG_PATH = "../config/" #change to your liking if forked.

def setup_logging():
    """Set up the logging configuration from the logging YAML file.

    This sets up various loggers, by different names with different settings,
    to be used throughout the program.  If the logger cannot be created, the
    root logger is still configured.  While this functionality is not optimal
    - logs will not be written to a file - it will not break the program in
    any part, since named loggers will simply be children of the root logger.

    Against some recommendations, loggers are not named after the __name__
    variable.  Instead, there are a few loggers of interest:

    1. rh_logger: the logger for the Reddit handler.  Debug and higher messages
                  go to a RotatingFileHandler with a 10kb cap and 1 backup.
                  Warning and higher messages go to sys.stderr.
    2. db_logger: the logger for the database handler.  Same as rh_logger, but
                  5 backups are kept.
    3. ex_logger: no backups are kept, and no messages are printed to the
                  console.
    3. root: only warning messages and higher, sent to the console.  Used
             only if other loggers cannot be found.

    For testing other modules, this function can be imported on its own to
    set up logging independently."""
    try:
        #imported here to export to other modules for testing
        import logging.config
        import yaml

        with open("{}logging.yml".format(CFG_PATH), "rt") as log_yaml:
            log_config = yaml.safe_load(log_yaml)
        logging.config.dictConfig(log_config)
        return
        #gather the logger from wherever you want in the program - it should
        #work with just the right name
    except ImportError as e:
        logging.error("ImportError {}: using root logger".format(e.message))
    except OSError as e:
        logging.error("OSError {}: using root logger".format(e.message))
    except:
        logging.error("Unexpected error configuring logging; using root "
                      "logger", exc_info=True)
    finally:
        #performed only when an exception occurs, but regardless of which
        #one occurs
        #Have to re-import logging to avoid UnboundLocalError
        import logging
        #Root logger set up for further use
        logging.basicConfig(datefmt="%Y/%m/%d %H:%M:%S",
                   format="%(asctime)s:%(name)s:%(levelname)s:%(message)s")

def print_post(post):
    """Prints a comment or post, with relevant information.  Used for
    testing, and to be deprecated."""
    logger = logging.getLogger("rh_logger")
    logger.debug("Printing post {!s}".format(post))
    if type(post) is not PRAW_COMMENT and type(post) is not PRAW_SUBMISSION:
        logger.error("Post {} is neither comment nor submission".format(post))
        return
    print("id: {}".format(post.id))
    print("author.name: {}".format(post.author.name))
    logger.debug("permalink: {}".format(post.permalink))
    logger.debug("created_utc (converted): {}".format(
        str(datetime.datetime.fromtimestamp(post.created_utc))))
    if type(post) is PRAW_COMMENT:
        print("body: {}".format(post.body), end="\n\n", flush=True)
    elif type(post) is PRAW_SUBMISSION:
        if post.is_self:
            print("selftext: {}".format(post.selftext), flush=True)
        else:
            print("url: {}".format(post.url), flush=True)

def main():
    """The main function of THE-equity-bot, it instantiates everything and
    begins to perform the bots function: monitor submissions, submissions and
    inbox messages,  parse them for requests, and replies with equity analyses
    as needed."""
    #Set ups: Set up Reddit praw instance, subreddit (list), database handler,
    #executable
    setup_logging()
    logger = logging.getLogger("rh_logger")
    logger.info("Logging configured and initiated.")
    reddit = praw.Reddit('THE-equity-bot')
    logger.info("Reddit instance obtained.")

    comment = reddit.comment('egezxul')
    print_post(comment)
    logger.debug("post printed")
    #Next: set up stream, check inbox, perform wake-up tests if needed.

    #Final: begin monitoring all comments/submissions/messages.  Loop until
    #shutdown sequence given.

    #Quitting: If shutdown sequence given or some other reason necessary to
    #fail out, finish all logging and db inquiries, clean up and quit.
    pass

if __name__ == "__main__":
    main()
